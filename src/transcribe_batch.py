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
    from src.utils.paths import ensure_output_dirs, get_output_paths
    from src.utils.supported_formats import (
        SUPPORTED_AUDIO_EXTENSIONS,
        is_supported_audio_file,
    )
    from src.utils.timestamps import format_timestamp
except ModuleNotFoundError:
    from utils.paths import ensure_output_dirs, get_output_paths
    from utils.supported_formats import (
        SUPPORTED_AUDIO_EXTENSIONS,
        is_supported_audio_file,
    )
    from utils.timestamps import format_timestamp

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster_whisper not installed. Run: pip install faster-whisper")
    sys.exit(1)


def transcribe_single(audio_path, model, args):
    """
    Transcribe a single audio file using an already loaded WhisperModel.
    Returns True on success, False on failure.
    """
    # 1. Ensure output directories exist
    ensure_output_dirs()

    # 2. Determine output paths
    txt_path, md_path = get_output_paths(audio_path)

    # 3. Check if outputs already exist (unless --overwrite)
    if not args.overwrite and (txt_path.exists() or md_path.exists()):
        print(
            f"  Skipping {audio_path.name}: output already exists. Use --overwrite to regenerate.")
        return None  # special value to indicate skipped

    print(f"  Transcribing '{audio_path.name}'...")
    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=args.language if args.language != "auto" else None,
            beam_size=5,
            vad_filter=True,
        )
    except Exception as e:
        print(f"  Transcription failed: {e}")
        return False

    # Collect segments
    segment_list = []
    for seg in segments:
        start_fmt = format_timestamp(seg.start)
        end_fmt = format_timestamp(seg.end)
        line = f"[{start_fmt} - {end_fmt}] {seg.text.strip()}"
        segment_list.append((seg.start, seg.end, seg.text.strip(), line))

    # Write plain text transcript
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Transcript of: {audio_path.name}\n")
        f.write(f"Language: {info.language}\n")
        f.write(f"Duration: {info.duration:.2f} seconds\n")
        f.write("=" * 50 + "\n")
        for _, _, _, line in segment_list:
            f.write(line + "\n")

    # Write markdown transcript
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Transcript: {audio_path.name}\n\n")
        f.write("## Metadata\n\n")
        f.write(f"- Source file: `{audio_path}`\n")
        f.write(f"- Language: `{info.language}`\n")
        f.write(f"- Duration: `{info.duration:.2f}` seconds\n")
        f.write(f"- Model: `{args.model}`\n")
        f.write(f"- Device: `{args.device}`\n")
        f.write(f"- Compute type: `{args.compute_type}`\n")
        f.write(
            f"- Detected language probability: `{info.language_probability:.2f}`\n\n")
        f.write("## Transcript\n\n")
        for _, _, text, line in segment_list:
            f.write(line + "\n\n")

    print(f"    Saved: {txt_path.name}, {md_path.name}")
    return True


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
        result = transcribe_single(audio_path, model, args)
        if result is None:
            skipped += 1
        elif result is True:
            processed += 1
        else:
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
