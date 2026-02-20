import random
from pathlib import Path

def scan_video(path: Path, temp_dir: Path) -> dict:
    """
    Analyse a video for deepfake manipulation.
    Replace this body with a real model (e.g. FaceForensics++).
    """
    penalty = random.randint(0, 60)
    is_fake = penalty > 30

    flags = []
    evidence = []

    if is_fake:
        flags.append("video:facial_inconsistency")
        flags.append("video:temporal_artifact")
        evidence.append({
            "pipeline": "video",
            "type": "deepfake_detection",
            "severity": 4,
            "details": {
                "facial_inconsistency": round(random.uniform(0.5, 0.95), 4),
                "temporal_artifacts":   round(random.uniform(0.4, 0.90), 4),
                "lip_sync_mismatch":    round(random.uniform(0.3, 0.85), 4),
            },
            "timestamps": []
        })

    # Clean up uploaded file
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "penalty": penalty,
        "flags": flags,
        "evidence": evidence,
        "summary": {
            "facial_inconsistency": round(random.uniform(0.5, 0.95) if is_fake else random.uniform(0.01, 0.2), 4),
            "temporal_artifacts":   round(random.uniform(0.4, 0.90) if is_fake else random.uniform(0.01, 0.2), 4),
            "lip_sync_mismatch":    round(random.uniform(0.3, 0.85) if is_fake else random.uniform(0.01, 0.2), 4),
        }
    }
