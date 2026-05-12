#!/usr/bin/env python3
"""FFmpeg discovery helpers."""

from pathlib import Path
import shutil


def find_ffmpeg() -> Path | None:
    """Find FFmpeg executable.

    Search order:
    1. tools/ffmpeg/ffmpeg.exe
    2. ffmpeg from PATH
    """
    local_ffmpeg = Path("tools") / "ffmpeg" / "ffmpeg.exe"
    if local_ffmpeg.is_file():
        return local_ffmpeg.resolve()

    ffmpeg_from_path = shutil.which("ffmpeg")
    if ffmpeg_from_path:
        return Path(ffmpeg_from_path).resolve()

    return None


def check_ffmpeg_available() -> bool:
    """Return True when FFmpeg is available."""
    return find_ffmpeg() is not None
