#!/usr/bin/env python3
"""
Single-audio-file transcription script using faster-whisper.
Stage 1 of GPT Course Knowledge Extractor.
"""

import argparse
import sys
from pathlib import Path
from datetime import timedelta

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster_whisper not installed. Run: pip install faster-whisper")
    sys.exit(1)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string."""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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

    args = parser.parse_args()

    audio_path = Path(args.audio_file).resolve()
    if not audio_path.exists():
        print(f"Error: File '{audio_path}' does not exist.")
        sys.exit(1)

    # Prepare output directories
    output_dir = Path("output")
    transcripts_dir = output_dir / "transcripts"
    markdown_dir = output_dir / "markdown"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    stem = audio_path.stem
    txt_path = transcripts_dir / f"{stem}.txt"
    md_path = markdown_dir / f"{stem}.md"

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
