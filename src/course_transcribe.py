#!/usr/bin/env python3
"""
Course‑aware batch transcription wrapper.

Stage 5.2 of GPT Course Knowledge Extractor.
Transcribes all audio/video files in a course's input/audio folder,
writing outputs to the course‑specific output directories.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.course_paths import get_course_paths
    from src.utils.supported_formats import (
        SUPPORTED_AUDIO_EXTENSIONS,
        is_supported_audio_file,
    )
except ModuleNotFoundError:
    from course_paths import get_course_paths
    from utils.supported_formats import (
        SUPPORTED_AUDIO_EXTENSIONS,
        is_supported_audio_file,
    )

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster_whisper not installed. Run: pip install faster-whisper")
    sys.exit(1)

try:
    from src.transcription_engine import transcribe_file
except ModuleNotFoundError:
    from transcription_engine import transcribe_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe all audio/video files in a course's input/audio folder.",
        epilog="Example: python -m src.course_transcribe test_course --overwrite",
    )
    parser.add_argument(
        "course_slug",
        help="Course identifier (slug) as used in courses/ directory.",
    )
    parser.add_argument(
        "--courses-dir",
        default="courses",
        help="Directory containing course workspaces (default: 'courses').",
    )
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model size (tiny, base, small, medium, large-v2, etc.)",
    )
    parser.add_argument(
        "--language",
        default="ru",
        help="Language code (e.g., 'ru', 'en', 'auto' for automatic detection)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Device to run inference on ('cpu', 'cuda', 'auto')",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Compute type for quantization (int8, float16, float32)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files. If not set, files with existing outputs are skipped.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders of input/audio recursively.",
    )

    args = parser.parse_args()

    # 1. Get course paths (validation happens inside)
    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    input_audio_dir = paths["input_audio"]
    transcripts_dir = paths["output_transcripts"]
    markdown_dir = paths["output_markdown"]

    # 2. Check that input directory exists (it should, because workspace is valid)
    if not input_audio_dir.is_dir():
        print(
            f"Info: Course input audio directory '{input_audio_dir}' does not exist.")
        print("      No audio/video files to transcribe.")
        sys.exit(0)

    # 3. Discover supported files
    pattern = "**/*" if args.recursive else "*"
    discovered = []
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        discovered.extend(input_audio_dir.glob(f"{pattern}{ext}"))

    # Filter out directories and ensure they are supported files
    supported_files = [
        f for f in discovered
        if f.is_file() and is_supported_audio_file(f)
    ]
    supported_files.sort(key=lambda p: str(p).lower())

    if not supported_files:
        print(f"No supported audio/video files found in '{input_audio_dir}'.")
        print(
            f"Supported extensions: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}")
        sys.exit(0)

    print(
        f"Found {len(supported_files)} supported file(s) in course '{args.course_slug}'.")
    print(f"Transcripts will be written to:")
    print(f"  TXT: {transcripts_dir}")
    print(f"  MD:  {markdown_dir}")

    # 4. Load model once
    print(f"Loading model '{args.model}' on {args.device}...")
    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
        )
    except Exception as e:
        print(f"Failed to load model: {e}")
        sys.exit(1)

    # 5. Process each file
    processed = 0
    skipped = 0
    failed = 0

    for idx, audio_path in enumerate(supported_files, start=1):
        print(f"[{idx}/{len(supported_files)}] {audio_path.name}")
        status = transcribe_file(
            audio_path=audio_path,
            model=model,
            model_name=args.model,
            language=args.language,
            device=args.device,
            compute_type=args.compute_type,
            overwrite=args.overwrite,
            print_segments=False,  # avoid flooding console in batch mode
            transcripts_dir=transcripts_dir,
            markdown_dir=markdown_dir,
        )
        if status == "processed":
            processed += 1
        elif status == "skipped":
            skipped += 1
        else:  # failed
            failed += 1
        print()  # empty line for readability

    # 6. Summary
    print("=" * 50)
    print("Course batch transcription completed.")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
