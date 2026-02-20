from pathlib import Path
import wave

import numpy as np

try:
    import atrust_native  # type: ignore
except ImportError:
    atrust_native = None

try:
    import torch
    import soundfile as sf
    from scipy.signal import resample_poly
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
except ImportError:
    torch = None
    sf = None
    resample_poly = None
    Wav2Vec2ForCTC = None
    Wav2Vec2Processor = None

WAV2VEC2_MODEL_ID = "facebook/wav2vec2-base-960h"
_processor = None
_model = None


def _load_wav2vec2_model():
    global _processor, _model

    if _processor is not None and _model is not None:
        return _processor, _model

    if Wav2Vec2Processor is None or Wav2Vec2ForCTC is None or torch is None:
        return None, None

    try:
        _processor = Wav2Vec2Processor.from_pretrained(WAV2VEC2_MODEL_ID)
        _model = Wav2Vec2ForCTC.from_pretrained(WAV2VEC2_MODEL_ID)
        _model.eval()
    except Exception:
        return None, None

    return _processor, _model


def _read_audio_16k(audio_path: Path):
    if sf is None:
        return None

    try:
        samples, sample_rate = sf.read(str(audio_path), always_2d=False)
    except Exception:
        return None

    if isinstance(samples, np.ndarray) and samples.ndim > 1:
        samples = np.mean(samples, axis=1)

    if sample_rate != 16000:
        if resample_poly is None:
            return None
        samples = resample_poly(samples, 16000, sample_rate)

    samples = np.asarray(samples, dtype=np.float32)
    peak = np.max(np.abs(samples)) if samples.size else 0.0
    if peak > 1.0:
        samples = samples / peak

    return samples


def _wav2vec2_voice_detection(audio_path: Path):
    processor, model = _load_wav2vec2_model()
    if processor is None or model is None:
        return None

    samples = _read_audio_16k(audio_path)
    if samples is None or samples.size == 0:
        return None

    with torch.no_grad():
        inputs = processor(samples, sampling_rate=16000, return_tensors="pt")
        logits = model(inputs.input_values).logits[0]

    probs = torch.softmax(logits, dim=-1)
    max_probs, pred_ids = torch.max(probs, dim=-1)
    blank_token_id = processor.tokenizer.pad_token_id

    speech_frames = pred_ids != blank_token_id
    speech_ratio = float(torch.mean(speech_frames.float()).item())
    frame_confidence = float(torch.mean(max_probs).item())

    voice_probability = max(0.0, min(1.0, (speech_ratio * 0.7) + (frame_confidence * 0.3)))
    anomaly_score = 1.0 - voice_probability

    return {
        "anomaly": anomaly_score,
        "voice_probability": voice_probability,
        "speech_ratio": speech_ratio,
        "frame_confidence": frame_confidence,
        "model": WAV2VEC2_MODEL_ID,
        "fallback": False,
    }


def _energy_fallback(audio_path: Path):
    try:
        with wave.open(str(audio_path), "rb") as wav:
            frames = wav.readframes(wav.getnframes())
        data = np.frombuffer(frames, dtype=np.int16)
        energy = float(np.mean(np.abs(data))) if data.size else 0.0
        return {
            "anomaly": max(0.0, min(1.0, energy / 8000.0)),
            "fallback": True,
            "model": "energy_heuristic",
        }
    except Exception:
        return {
            "anomaly": 0.0,
            "fallback": True,
            "error": "unreadable_audio",
            "model": "energy_heuristic",
        }


def scan_audio(audio_path: Path):
    if atrust_native is not None and hasattr(atrust_native, "audio_anomaly_score"):
        out = atrust_native.audio_anomaly_score(str(audio_path))
    else:
        out = _wav2vec2_voice_detection(audio_path)
        if out is None:
            out = _energy_fallback(audio_path)

    score = float(out.get("anomaly", 0.0))

    penalty = int(score * 50)
    flags = []
    evidence = []

    if score >= 0.75:
        flags.append("audio:high_anomaly")
        evidence.append(
            {
                "pipeline": "audio",
                "type": "voice_detection_anomaly",
                "severity": 4,
                "details": out,
                "timestamps": [],
            }
        )
    elif score >= 0.5:
        flags.append("audio:medium_anomaly")
        evidence.append(
            {
                "pipeline": "audio",
                "type": "voice_detection_anomaly",
                "severity": 3,
                "details": out,
                "timestamps": [],
            }
        )

    return {"penalty": min(penalty, 50), "flags": flags, "evidence": evidence, "summary": out}
