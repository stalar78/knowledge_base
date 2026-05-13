#!/usr/bin/env python3
"""Extract MP3 audio from video files using FFmpeg."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    from src.ffmpeg_utils import find_ffmpeg
except ModuleNotFoundError:
    from ffmpeg_utils import find_ffmpeg

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".flv"}


def is_supported_video_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS


def discover_video_files(input_path: Path, recursive: bool = False) -> list[Path]:
    if input_path.is_file():
        return [input_path] if is_supported_video_file(input_path) else []

    if not input_path.is_dir():
        return []

    pattern = "**/*" if recursive else "*"
    files = [p for p in input_path.glob(pattern) if is_supported_video_file(p)]
    files.sort(key=lambda p: str(p).lower())
    return files


def get_subprocess_startup_kwargs() -> dict:
    if os.name != "nt":
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


def extract_audio_file(
    video_path: Path,
    output_dir: Path,
    ffmpeg_path: Path,
    bitrate: str = "192k",
    overwrite: bool = False,
) -> str:
    """Extract MP3 from one video file.

    Returns: "processed", "skipped", or "failed".
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{video_path.stem}.mp3"

    if output_path.exists() and not overwrite:
        return "skipped"

    overwrite_flag = "-y" if overwrite else "-n"
    cmd = [
        str(ffmpeg_path),
        overwrite_flag,
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-b:a",
        bitrate,
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            **get_subprocess_startup_kwargs(),
        )
    except Exception as exc:
        print(f"Failed to run FFmpeg for '{video_path.name}': {exc}", file=sys.stderr)
        return "failed"

    if result.returncode == 0:
        return "processed"

    stderr = (result.stderr or "").strip()
    if stderr:
        print(f"FFmpeg failed for '{video_path.name}':\n{stderr}", file=sys.stderr)
    else:
        print(f"FFmpeg failed for '{video_path.name}'.", file=sys.stderr)
    return "failed"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract MP3 audio from video file(s) using FFmpeg.",
        epilog="Example: python -m src.extract_audio courses/test/input/video --recursive --overwrite",
    )
    parser.add_argument("input_path", help="Path to input video file or folder.")
    parser.add_argument(
        "--output-dir",
        default="output/audio",
        help="Directory for extracted MP3 files (default: output/audio).",
    )
    parser.add_argument("--recursive", action="store_true", help="Scan subfolders recursively.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing MP3 files.")
    parser.add_argument("--bitrate", default="192k", help="Output MP3 bitrate (default: 192k).")
    args = parser.parse_args()

    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        print("FFmpeg not found.")
        print("Put ffmpeg.exe into tools/ffmpeg/ffmpeg.exe or install FFmpeg into PATH.")
        sys.exit(1)

    input_path = Path(args.input_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    files = discover_video_files(input_path, recursive=args.recursive)
    if not files:
        print(f"No supported video files found in '{input_path}'.")
        print(f"Supported extensions: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        sys.exit(0)

    processed = 0
    skipped = 0
    failed = 0

    for idx, video_path in enumerate(files, start=1):
        print(f"[{idx}/{len(files)}] Extracting audio from {video_path.name}")
        status = extract_audio_file(
            video_path=video_path,
            output_dir=output_dir,
            ffmpeg_path=ffmpeg_path,
            bitrate=args.bitrate,
            overwrite=args.overwrite,
        )
        if status == "processed":
            processed += 1
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    print("=" * 50)
    print("Audio extraction completed.")
    print(f"  processed: {processed}")
    print(f"  skipped:   {skipped}")
    print(f"  failed:    {failed}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
