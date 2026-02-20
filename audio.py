import random
from pathlib import Path

def scan_audio(path: Path) -> dict:
    """
    Detect voice cloning or audio manipulation.
    Replace this body with a real model (e.g. RawNet2, AASIST).
    """
    penalty = random.randint(0, 60)
    is_cloned = penalty > 30

    flags = []
    evidence = []

    if is_cloned:
        flags.append("audio:spectral_anomaly")
        flags.append("audio:prosody_mismatch")
        evidence.append({
            "pipeline": "audio",
            "type": "voice_clone_detection",
            "severity": 4,
            "details": {
                "spectral_anomaly":    round(random.uniform(0.5, 0.95), 4),
                "prosody_mismatch":    round(random.uniform(0.4, 0.90), 4),
                "voice_similarity":    round(random.uniform(0.5, 0.98), 4),
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
            "spectral_anomaly":  round(random.uniform(0.5, 0.95) if is_cloned else random.uniform(0.01, 0.2), 4),
            "prosody_mismatch":  round(random.uniform(0.4, 0.90) if is_cloned else random.uniform(0.01, 0.2), 4),
            "voice_similarity":  round(random.uniform(0.5, 0.98) if is_cloned else random.uniform(0.01, 0.2), 4),
        }
    }
