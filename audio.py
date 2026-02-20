from pathlib import Path
import atrust_native  # type: ignore

def scan_audio(audio_path: Path):
    # C++ computes spectral metrics, returns anomaly score 0..1
    out = atrust_native.audio_anomaly_score(str(audio_path))
    score = float(out.get("anomaly", 0.0))

    penalty = int(score * 50)
    flags = []
    evidence = []

    if score >= 0.75:
        flags.append("audio:high_anomaly")
        evidence.append({
            "pipeline": "audio",
            "type": "spectral_anomaly",
            "severity": 4,
            "details": out,
            "timestamps": []
        })
    elif score >= 0.5:
        flags.append("audio:medium_anomaly")
        evidence.append({
            "pipeline": "audio",
            "type": "spectral_anomaly",
            "severity": 3,
            "details": out,
            "timestamps": []
        })

    return {"penalty": min(penalty, 50), "flags": flags, "evidence": evidence, "summary": out}
