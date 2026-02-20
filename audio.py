from pathlib import Path
import wave
import numpy as np

try:
    import atrust_native  # type: ignore
except ImportError:
    atrust_native = None
def scan_audio(audio_path: Path):
    if atrust_native is not None and hasattr(atrust_native, "audio_anomaly_score"):
        out = atrust_native.audio_anomaly_score(str(audio_path))
    else:
        try:
            with wave.open(str(audio_path), "rb") as wav:
                frames = wav.readframes(wav.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            energy = float(np.mean(np.abs(data))) if data.size else 0.0
            out = {
                "anomaly": max(0.0, min(1.0, energy / 8000.0)),
                "fallback": True,
            }
        except Exception:
            out = {"anomaly": 0.0, "fallback": True, "error": "unreadable_audio"}

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
