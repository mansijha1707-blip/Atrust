from pathlib import Path
import numpy as np
import wave

try:
    import torch
    import soundfile as sf
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

WAV2VEC2_MODEL_ID = "facebook/wav2vec2-base-960h"
_processor = None
_model = None

def _load_model():
    global _processor, _model
    if _processor is not None:
        return _processor, _model
    try:
        _processor = Wav2Vec2Processor.from_pretrained(WAV2VEC2_MODEL_ID)
        _model = Wav2Vec2ForCTC.from_pretrained(WAV2VEC2_MODEL_ID)
        _model.eval()
    except Exception:
        return None, None
    return _processor, _model

def _energy_fallback(audio_path: Path) -> float:
    """Simple energy-based anomaly score — works without torch."""
    try:
        with wave.open(str(audio_path), "rb") as wav:
            frames = wav.readframes(wav.getnframes())
        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if data.size == 0:
            return 0.0
        # Normalise energy to 0-1 range
        energy = float(np.mean(np.abs(data)))
        score = max(0.0, min(1.0, 1.0 - (energy / 8000.0)))
        return score
    except Exception:
        return 0.5

def _wav2vec2_score(audio_path: Path) -> float:
    """Use Wav2Vec2 entropy as anomaly signal."""
    processor, model = _load_model()
    if processor is None or model is None:
        return None
    try:
        import soundfile as sf
        samples, sr = sf.read(str(audio_path), always_2d=False)
        if samples.ndim > 1:
            samples = np.mean(samples, axis=1)
        samples = np.asarray(samples, dtype=np.float32)
        inputs = processor(samples, sampling_rate=sr, return_tensors="pt")
        with torch.no_grad():
            logits = model(inputs.input_values).logits[0]
        probs = torch.softmax(logits, dim=-1)
        # Use entropy as anomaly signal — same approach as image.py
        entropy = -float(torch.sum(probs * torch.log(probs + 1e-8)).item())
        score = min(1.0, entropy / 6.0)
        return score
    except Exception:
        return None

def scan_audio(audio_path: Path) -> dict:
    # Try real model first, fall back to energy heuristic
    if TORCH_AVAILABLE:
        score = _wav2vec2_score(audio_path)
    else:
        score = None

    if score is None:
        score = _energy_fallback(audio_path)

    penalty = int(score * 50)
    flags = []
    evidence = []

    if score >= 0.75:
        flags.append("audio:high_anomaly")
        evidence.append({
            "pipeline": "audio",
            "type": "voice_detection_anomaly",
            "severity": 4,
            "details": {"score": score},
            "timestamps": []
        })
    elif score >= 0.5:
        flags.append("audio:medium_anomaly")
        evidence.append({
            "pipeline": "audio",
            "type": "voice_detection_anomaly",
            "severity": 3,
            "details": {"score": score},
            "timestamps": []
        })

    try:
        audio_path.unlink(missing_ok=True)
    except Exception:
        pass

    return {
        "penalty": min(penalty, 50),
        "flags": flags,
        "evidence": evidence,
        "summary": {"score": score}
    }
