from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

def _read_exif(path: Path):
    try:
        img = Image.open(path)
        exif_data = img.getexif()
        out = {}
        for k, v in exif_data.items():
            out[TAGS.get(k, str(k))] = str(v)
        return out
    except Exception:
        return {}

def scan_image(image_path: Path):
    img = cv2.imread(str(image_path))
    penalty = 0
    flags = []
    evidence = []

    if img is None:
        return {"penalty": 30, "flags": ["image:unreadable"], "evidence": [{
            "pipeline": "image", "type": "unreadable_file", "severity": 4, "details": {}
        }]}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # crude artifact proxies
    if lap_var < 40:
        penalty += 10
        flags.append("image:very_blurry")

    exif = _read_exif(image_path)
    if not exif:
        penalty += 4
        flags.append("image:missing_metadata")

    # Example: suspicious software tags (basic rule)
    software = (exif.get("Software", "") or "").lower()
    if any(x in software for x in ["photoshop", "gimp", "stable diffusion", "midjourney", "comfyui"]):
        penalty += 8
        flags.append("image:edited_software_tag")
        evidence.append({
            "pipeline": "image",
            "type": "metadata_edit_software",
            "severity": 3,
            "details": {"Software": exif.get("Software", "")},
            "timestamps": []
        })

    return {
        "penalty": min(penalty, 40),
        "flags": flags,
        "evidence": evidence,
        "summary": {"laplacian_var": float(lap_var), "has_exif": bool(exif)}
    }
