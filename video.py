from pathlib import Path
import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0
from PIL import Image
import cv2
import numpy as np

video_model = efficientnet_b0(pretrained=True)
video_model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def scan_video(path: Path, temp_dir: Path) -> dict:
    # Extract frames
    cap = cv2.VideoCapture(str(path))
    frames = []
    frame_count = 0
    success = True
    while success and frame_count < 16:
        success, frame = cap.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
            frame_count += 1
    cap.release()

    if not frames:
        score = 0.0
    else:
        scores = []
        for img in frames:
            x = transform(img).unsqueeze(0)
            with torch.no_grad():
                out = video_model(x)
                prob = torch.nn.functional.softmax(out, dim=1)
                # Use entropy as anomaly signal — same as image.py
                entropy = -float(torch.sum(prob * torch.log(prob + 1e-8)).item())
                frame_score = min(1.0, entropy / 6.0)
                scores.append(frame_score)
        score = float(np.mean(scores))

    penalty = int(score * 50)
    flags = []
    evidence = []

    if score >= 0.75:
        flags.append("video:facial_inconsistency")
        flags.append("video:temporal_artifact")
        evidence.append({
            "pipeline": "video",
            "type": "deepfake_detection",
            "severity": 4,
            "details": {"score": score},
            "timestamps": [],
        })
    elif score >= 0.5:
        flags.append("video:facial_inconsistency")
        evidence.append({
            "pipeline": "video",
            "type": "deepfake_detection",
            "severity": 3,
            "details": {"score": score},
            "timestamps": [],
        })

    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "penalty": min(penalty, 50),
        "flags": flags,
        "evidence": evidence,
        "summary": {"score": score}
    }
