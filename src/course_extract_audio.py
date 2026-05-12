#!/usr/bin/env python3
"""Course-aware video-to-MP3 extraction wrapper."""

import argparse
import sys
from pathlib import Path

try:
    from src.course_paths import get_course_paths
    from src.extract_audio import discover_video_files, extract_audio_file
    from src.ffmpeg_utils import find_ffmpeg
except ModuleNotFoundError:
    from course_paths import get_course_paths
    from extract_audio import discover_video_files, extract_audio_file
    from ffmpeg_utils import find_ffmpeg


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
    args = parser.parse_args()

    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path is None:
        print("FFmpeg not found.")
        print("Put ffmpeg.exe into tools/ffmpeg/ffmpeg.exe or install FFmpeg into PATH.")
        sys.exit(1)

    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    input_video_dir = paths["input_video"]
    output_audio_dir = paths["input_audio"]

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
