#!/usr/bin/env python3
"""FFmpeg discovery helpers."""

from pathlib import Path
import shutil

try:
    from src.runtime_environment import get_app_base_dir, is_frozen
except ModuleNotFoundError:
    from runtime_environment import get_app_base_dir, is_frozen


def find_ffmpeg() -> Path | None:
    """Find FFmpeg executable.

    Search order:
    1. tools/ffmpeg/ffmpeg.exe
    2. ffmpeg from PATH
    """
    # Frozen mode: prefer the folder next to the executable.
    if is_frozen():
        frozen_ffmpeg = get_app_base_dir() / "tools" / "ffmpeg" / "ffmpeg.exe"
        if frozen_ffmpeg.is_file():
            return frozen_ffmpeg.resolve()

    # Source mode (or fallback in frozen): project-relative path.
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
