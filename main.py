import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from files import save_upload
from report import build_trust_report
from text import scan_text

app = FastAPI(title="Atrust API", version="0.1.0")

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
_raw_origins = os.getenv("ATRUST_CORS_ORIGINS", ",".join(_default_origins))
allow_origins = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan/video")
@app.post("/api/scan/video")
def scan_video_ep(file: UploadFile = File(...)):
    from video import scan_video

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".mp4")
    with tempfile.TemporaryDirectory() as td:
        results = {"video": scan_video(path, Path(td))}
    return build_trust_report(results).model_dump()


@app.post("/scan/image")
@app.post("/api/scan/image")
def scan_image_ep(file: UploadFile = File(...)):
    from image import scan_image

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".jpg")
    results = {"image": scan_image(path)}
    return build_trust_report(results).model_dump()


@app.post("/scan/audio")
@app.post("/api/scan/audio")
def scan_audio_ep(file: UploadFile = File(...)):
    from audio import scan_audio

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".wav")
    results = {"audio": scan_audio(path)}
    return build_trust_report(results).model_dump()


@app.post("/scan/text")
@app.post("/api/scan/text")
def scan_text_ep(text: str = Form(...)):
    results = {"text": scan_text(text)}
    return build_trust_report(results).model_dump()


@app.post("/scan/unified")
@app.post("/api/scan/unified")
def scan_unified(
    video: UploadFile | None = File(None),
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    text: str | None = Form(None),
):
    results = {}
    if video:
        from video import scan_video

        vpath = save_upload(video.file, suffix=Path(video.filename).suffix or ".mp4")
        with tempfile.TemporaryDirectory() as td:
            results["video"] = scan_video(vpath, Path(td))
    if image:
        from image import scan_image

        ipath = save_upload(image.file, suffix=Path(image.filename).suffix or ".jpg")
        results["image"] = scan_image(ipath)
    if audio:
        from audio import scan_audio

        apath = save_upload(audio.file, suffix=Path(audio.filename).suffix or ".wav")
        results["audio"] = scan_audio(apath)
    if text:
        results["text"] = scan_text(text)

    return build_trust_report(results).model_dump()
