from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile

from files import save_upload
from text import scan_text
from report import build_trust_report

app = FastAPI(title="Atrust API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/scan/video")
def scan_video_ep(file: UploadFile = File(...)):
    from video import scan_video

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".mp4")
    with tempfile.TemporaryDirectory() as td:
        results = {"video": scan_video(path, Path(td))}
    return build_trust_report(results).model_dump()

@app.post("/scan/image")
def scan_image_ep(file: UploadFile = File(...)):
    from image import scan_image

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".jpg")
    results = {"image": scan_image(path)}
    return build_trust_report(results).model_dump()

@app.post("/scan/audio")
def scan_audio_ep(file: UploadFile = File(...)):
    from audio import scan_audio

    path = save_upload(file.file, suffix=Path(file.filename).suffix or ".wav")
    results = {"audio": scan_audio(path)}
    return build_trust_report(results).model_dump()

@app.post("/scan/text")
def scan_text_ep(text: str = Form(...)):
    results = {"text": scan_text(text)}
    return build_trust_report(results).model_dump()

@app.post("/scan/unified")
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
