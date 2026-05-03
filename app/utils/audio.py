import shutil
import subprocess
import uuid
from pathlib import Path

from app.core.config import settings

ALLOWED_AUDIO_SUFFIXES = {".wav", ".webm", ".mp3", ".m4a", ".ogg"}


def ensure_ffmpeg() -> str:
    ffmpeg_binary = settings.FFMPEG_PATH
    if shutil.which(ffmpeg_binary):
        return ffmpeg_binary
    if Path(ffmpeg_binary).exists():
        return ffmpeg_binary
    raise RuntimeError(f"ffmpeg 不可用: {ffmpeg_binary}")


def convert_to_wav(file_bytes: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower() or ".webm"
    if suffix not in ALLOWED_AUDIO_SUFFIXES:
        raise RuntimeError(f"不支持的音频格式: {suffix}")

    ffmpeg_binary = ensure_ffmpeg()
    file_id = uuid.uuid4().hex
    source_path = settings.TEMP_DIR / f"{file_id}{suffix}"
    target_path = settings.TEMP_DIR / f"{file_id}.wav"

    source_path.write_bytes(file_bytes)

    try:
        subprocess.run(
            [ffmpeg_binary, "-i", str(source_path), "-ar", "16000", "-ac", "1", "-y", str(target_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return str(target_path)
    finally:
        source_path.unlink(missing_ok=True)
