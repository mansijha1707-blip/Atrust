import random
from pathlib import Path

def scan_image(path: Path) -> dict:
    """
    Detect AI-generated or manipulated images.
    Replace this body with a real model (e.g. CNNDetection, DIRE).
    """
    penalty = random.randint(0, 60)
    is_fake = penalty > 30

    flags = []
    evidence = []

    if is_fake:
        flags.append("image:gan_fingerprint")
        flags.append("image:noise_anomaly")
        evidence.append({
            "pipeline": "image",
            "type": "ai_image_detection",
            "severity": 4,
            "details": {
                "face_swap_probability": round(random.uniform(0.5, 0.95), 4),
                "noise_pattern_anomaly": round(random.uniform(0.4, 0.90), 4),
                "gan_fingerprint_score": round(random.uniform(0.5, 0.98), 4),
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
            "face_swap_probability": round(random.uniform(0.5, 0.95) if is_fake else random.uniform(0.01, 0.2), 4),
            "noise_pattern_anomaly": round(random.uniform(0.4, 0.90) if is_fake else random.uniform(0.01, 0.2), 4),
            "gan_fingerprint_score": round(random.uniform(0.5, 0.98) if is_fake else random.uniform(0.01, 0.2), 4),
        }
    }
