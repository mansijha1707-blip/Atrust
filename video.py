from pathlib import Path
import os
import cv2
import numpy as np
import mediapipe as mp

try:
    import tensorflow as tf
except ImportError:  # tensorflow is optional at runtime
    tf = None

from ..utils.ffmpeg import extract_frames

# native module (built from cpp/)

import atrust_native  # type: ignore


class XceptionDeepfakeDetector:
    """Loads a fine-tuned Xception deepfake classifier and scores face crops."""

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or os.getenv("ATRUST_XCEPTION_MODEL_PATH", "models/xception_deepfake.keras")
        self.model = None
        self.error = None

        if tf is None:
            self.error = "tensorflow_not_installed"
            return

        try:
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
        except Exception as exc:  # model file may be absent/corrupt
            self.error = f"model_load_failed:{type(exc).__name__}"

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    def predict_face_score(self, face_bgr: np.ndarray) -> float:
        if self.model is None:
            return 0.0

        rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (299, 299), interpolation=cv2.INTER_AREA)
        # Scale to [-1, 1] as expected by Xception preprocess
        x = tf.keras.applications.xception.preprocess_input(resized.astype(np.float32))
        x = np.expand_dims(x, axis=0)

        pred = self.model.predict(x, verbose=0)
        score = float(np.squeeze(pred))
        # Model outputs can be logits/probabilities; normalize to [0,1]
        if score < 0.0 or score > 1.0:
            score = float(1.0 / (1.0 + np.exp(-score)))
        return max(0.0, min(1.0, score))

def _artifact_score(img_bgr: np.ndarray) -> float:
    # Simple heuristic examples: blur, edge inconsistency, compression artifacts proxy
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()  # low => blurry
    # normalize-ish
    blur_score = max(0.0, min(1.0, (120.0 - lap_var) / 120.0))
    return float(blur_score)

def scan_video(video_path: Path, work_dir: Path, sample_fps: int = 2):␊
    frames_dir = work_dir / "frames"
    extract_frames(video_path, frames_dir, fps=sample_fps)

    mp_face = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    xception = XceptionDeepfakeDetector()

    frame_paths = sorted(frames_dir.glob("frame_*.jpg"))
    suspicious = []
    penalty = 0
    flags = []
    evidence = []

    for i, fp in enumerate(frame_paths):
        img = cv2.imread(str(fp))
        if img is None:
            continue

        # Face detect (MediaPipe expects RGB)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        det = mp_face.process(rgb)
        faces = det.detections or []␊

        if len(faces) == 0:
            # Not automatically malicious; small penalty only if many
            continue

        
        # Native fast metrics
        # returns dict: {"blockiness":..., "noise":..., "sharpness":...}
        metrics = atrust_native.frame_metrics(img)  # numpy array -> C++

        face_scores = []
        for face in faces:
            box = face.location_data.relative_bounding_box
            h, w = img.shape[:2]
            x1 = max(0, int(box.xmin * w))
            y1 = max(0, int(box.ymin * h))
            x2 = min(w, x1 + int(box.width * w))
            y2 = min(h, y1 + int(box.height * h))
            if x2 <= x1 or y2 <= y1:
                continue

            face_crop = img[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue

            face_scores.append(xception.predict_face_score(face_crop))

        xception_score = float(np.mean(face_scores)) if face_scores else 0.0

        art = _artifact_score(img)
        # example combined suspicion
        suspicion = 0.0
        suspicion += 0.35 * float(metrics.get("blockiness", 0.0))
        suspicion += 0.15 * float(metrics.get("noise", 0.0))
        suspicion += 0.15 * art
        suspicion += 0.35 * xception_score

        if suspicion >= 0.65:
            t = i / float(sample_fps)
            suspicious.append({"start": max(0.0, t - 0.25), "end": t + 0.25})
            penalty += 6
            flags.append("video:suspicious_frame_metrics")
            if xception_score >= 0.5:
                flags.append("video:xception_deepfake_high_confidence")

    if not xception.is_ready:
        flags.append(f"video:xception_unavailable:{xception.error}")

    if suspicious:
        evidence.append({
            "pipeline": "video",
            "type": "deepfake_suspected_segments",
            "severity": 4 if len(suspicious) >= 3 else 3,
            "details": {
                "sample_fps": sample_fps,
                "count": len(suspicious),
                "xception_enabled": xception.is_ready,
                "xception_model_path": xception.model_path,
            },
            "timestamps": suspicious
        })

    return {
        "penalty": min(penalty, 60),
        "flags": flags,
        "evidence": evidence,
        "summary": {"suspicious_segments": len(suspicious)}
    }
