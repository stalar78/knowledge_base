"""
Supported audio/video file extensions for faster-whisper.

Note: Some extensions are video containers, but faster-whisper (via ffmpeg)
can extract the audio stream from them. Dedicated video-to-audio extraction
will be handled separately in later stages.
"""

from pathlib import Path

SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg",
    ".webm",
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
}


def is_supported_audio_file(path: Path) -> bool:
    """
    Check if a file has a supported audio/video extension.

    Args:
        path: Path to the file.

    Returns:
        True if the file's suffix (case-insensitive) is in the supported set.
    """
    return path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS

