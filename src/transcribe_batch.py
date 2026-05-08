#!/usr/bin/env python3
"""
Batch transcription script for a folder of audio/video files.
Stage 2 of GPT Course Knowledge Extractor.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.utils.supported_formats import (
        SUPPORTED_AUDIO_EXTENSIONS,
        is_supported_audio_file,
    )
except ModuleNotFoundError:
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


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe all supported audio/video files in a folder using faster-whisper."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Path to the folder containing audio/video files (e.g., input/audio)",
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
        help="Scan subfolders recursively.",
    )

    args = parser.parse_args()

    folder_path = Path(args.folder).resolve()

    # 1. Check folder existence
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)

    # 2. Check that it's a directory
    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)

    # 3. Discover supported files
    pattern = "**/*" if args.recursive else "*"
    discovered = []
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        discovered.extend(folder_path.glob(f"{pattern}{ext}"))

    # Filter out directories (just in case) and ensure they are files
    supported_files = [f for f in discovered if f.is_file()
                       and is_supported_audio_file(f)]
    supported_files.sort(key=lambda p: str(p).lower())

    if not supported_files:
        print(f"No supported audio/video files found in '{folder_path}'.")
        print(
            f"Supported extensions: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}")
        sys.exit(0)

    print(f"Found {len(supported_files)} supported file(s).")

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
    print("Batch transcription completed.")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
