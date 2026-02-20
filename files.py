import os, uuid, shutil
from pathlib import Path

UPLOAD_DIR = Path(os.getenv("ATRUST_UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(file_obj, suffix: str) -> Path:
    fid = uuid.uuid4().hex
    path = UPLOAD_DIR / f"{fid}{suffix}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file_obj, f)
    return path
