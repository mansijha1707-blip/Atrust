from pathlib import Path
import cv2
import numpy as np
import mediapipe as mp

from ..utils.ffmpeg import extract_frames

# native module (built from cpp/)
import atrust_native  # type: ignore

def _artifact_score(img_bgr: np.ndarray) -> float:
    # Simple heuristic examples: blur, edge inconsistency, compression artifacts proxy
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()  # low => blurry
    # normalize-ish
    blur_score = max(0.0, min(1.0, (120.0 - lap_var) / 120.0))
    return float(blur_score)

def scan_video(video_path: Path, work_dir: Path, sample_fps: int = 2):
    frames_dir = work_dir / "frames"
    extract_frames(video_path, frames_dir, fps=sample_fps)

    mp_face = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

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
        faces = det.detections or []

        if len(faces) == 0:
            # Not automatically malicious; small penalty only if many
            continue

        # Native fast metrics
        # returns dict: {"blockiness":..., "noise":..., "sharpness":...}
        metrics = atrust_native.frame_metrics(img)  # numpy array -> C++

        art = _artifact_score(img)
        # example combined suspicion
        suspicion = 0.0
        suspicion += 0.55 * float(metrics.get("blockiness", 0.0))
        suspicion += 0.25 * float(metrics.get("noise", 0.0))
        suspicion += 0.20 * art

        if suspicion >= 0.65:
            t = i / float(sample_fps)
            suspicious.append({"start": max(0.0, t - 0.25), "end": t + 0.25})
            penalty += 6
            flags.append("video:suspicious_frame_metrics")

    if suspicious:
        evidence.append({
            "pipeline": "video",
            "type": "deepfake_suspected_segments",
            "severity": 4 if len(suspicious) >= 3 else 3,
            "details": {"sample_fps": sample_fps, "count": len(suspicious)},
            "timestamps": suspicious
        })

    return {
        "penalty": min(penalty, 60),
        "flags": flags,
        "evidence": evidence,
        "summary": {"suspicious_segments": len(suspicious)}
    }
