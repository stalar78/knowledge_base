#!/usr/bin/env python3
"""
Single-audio-file transcription script using faster-whisper.
Stage 1 of GPT Course Knowledge Extractor.
"""

import argparse
import sys
from pathlib import Path

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


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file using faster-whisper."
    )
    parser.add_argument(
        "audio_file",
        type=str,
        help="Path to the audio file (e.g., input/audio/lecture.mp3)",
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
        help="Overwrite existing output files. If not set, script will exit when outputs already exist.",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio_file).resolve()

    # 1. Check file existence
    if not audio_path.exists():
        print(f"Error: File '{audio_path}' does not exist.")
        sys.exit(1)

    # 2. Check supported extension
    if not is_supported_audio_file(audio_path):
        print(f"Error: Unsupported file extension '{audio_path.suffix}'.")
        supported = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        print(f"Supported extensions: {supported}")
        sys.exit(1)

    # 3. Ensure output directories exist
    ensure_output_dirs()

    # 4. Determine output paths
    txt_path, md_path = get_output_paths(audio_path)

    # 5. Check if outputs already exist (unless --overwrite)
    if not args.overwrite and (txt_path.exists() or md_path.exists()):
        print("Output files already exist:")
        if txt_path.exists():
            print(f"  - {txt_path}")
        if md_path.exists():
            print(f"  - {md_path}")
        print("Use --overwrite to regenerate them.")
        sys.exit(0)

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

    print(f"Transcribing '{audio_path.name}'...")
    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=args.language if args.language != "auto" else None,
            beam_size=5,
            vad_filter=True,
        )
    except Exception as e:
        print(f"Transcription failed: {e}")
        sys.exit(1)

    print(
        f"Detected language: {info.language}, probability: {info.language_probability:.2f}")
    print(f"Duration: {info.duration:.2f} seconds")

    # Collect segments
    segment_list = []
    for seg in segments:
        start_fmt = format_timestamp(seg.start)
        end_fmt = format_timestamp(seg.end)
        line = f"[{start_fmt} - {end_fmt}] {seg.text.strip()}"
        segment_list.append((seg.start, seg.end, seg.text.strip(), line))
        print(line)

    # Write plain text transcript
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Transcript of: {audio_path.name}\n")
        f.write(f"Language: {info.language}\n")
        f.write(f"Duration: {info.duration:.2f} seconds\n")
        f.write("=" * 50 + "\n")
        for _, _, _, line in segment_list:
            f.write(line + "\n")
    print(f"\nPlain text transcript saved to: {txt_path}")

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
    print(f"Markdown transcript saved to: {md_path}")


if __name__ == "__main__":
    main()
