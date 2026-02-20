import subprocess
from pathlib import Path

def extract_frames(video_path: Path, out_dir: Path, fps: int = 2) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # outputs frame_000001.jpg ...
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        str(out_dir / "frame_%06d.jpg")
    ]
    subprocess.run(cmd, check=True, capture_output=True)
