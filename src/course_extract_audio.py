#!/usr/bin/env python3
"""Course-aware video-to-MP3 extraction wrapper."""

import argparse
import sys
from pathlib import Path

try:
    from src.course_paths import get_course_paths
    from src.extract_audio import discover_video_files, extract_audio_file, is_supported_video_file
    from src.ffmpeg_utils import find_ffmpeg
except ModuleNotFoundError:
    from course_paths import get_course_paths
    from extract_audio import discover_video_files, extract_audio_file, is_supported_video_file
    from ffmpeg_utils import find_ffmpeg


def resolve_video_file_arg(file_arg: str, input_video_dir: Path) -> Path:
    candidate = Path(file_arg)
    if not candidate.is_absolute():
        candidate = input_video_dir / candidate
    candidate = candidate.resolve()
    input_video_dir_resolved = input_video_dir.resolve()

    try:
        candidate.relative_to(input_video_dir_resolved)
    except ValueError:
        raise ValueError(
            f"Selected file must be inside course input/video folder: {input_video_dir_resolved}"
        )

    if not candidate.is_file():
        raise ValueError(f"File does not exist: {candidate}")
    if not is_supported_video_file(candidate):
        raise ValueError(f"Unsupported video file: {candidate}")
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract MP3 audio from videos in a course workspace.",
        epilog="Example: python -m src.course_extract_audio test_course --overwrite",
    )
    parser.add_argument("course_slug", help="Course identifier (slug) as used in courses/ directory.")
    parser.add_argument(
        "--courses-dir",
        default="courses",
        help="Directory containing course workspaces (default: 'courses').",
    )
    parser.add_argument("--recursive", action="store_true", help="Scan subfolders recursively.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing MP3 files.")
    parser.add_argument("--bitrate", default="192k", help="Output MP3 bitrate (default: 192k).")
    parser.add_argument(
        "--file",
        help="Single video file to process (path relative to input/video or full path inside it).",
    )
    args = parser.parse_args()

    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        print("FFmpeg not found.")
        print("Put ffmpeg.exe into tools/ffmpeg/ffmpeg.exe or install FFmpeg into PATH.")
        sys.exit(1)

    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    input_video_dir = paths["input_video"]
    output_audio_dir = paths["input_audio"]

    if args.file:
        try:
            selected_file = resolve_video_file_arg(args.file, input_video_dir)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        files = [selected_file]
    else:
        files = discover_video_files(input_video_dir, recursive=args.recursive)
    if not files:
        print(f"No supported video files found in '{input_video_dir}'.")
        sys.exit(0)

    processed = 0
    skipped = 0
    failed = 0

    for idx, video_path in enumerate(files, start=1):
        print(f"[{idx}/{len(files)}] Extracting audio from {video_path.name}")
        status = extract_audio_file(
            video_path=video_path,
            output_dir=output_audio_dir,
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
    print("Course audio extraction completed.")
    print(f"  processed: {processed}")
    print(f"  skipped:   {skipped}")
    print(f"  failed:    {failed}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
