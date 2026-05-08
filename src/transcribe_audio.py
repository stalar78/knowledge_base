#!/usr/bin/env python3
"""
Single-audio-file transcription script using faster-whisper.
Stage 1 of GPT Course Knowledge Extractor.
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

    # Delegate transcription to the shared engine
    status = transcribe_file(
        audio_path=audio_path,
        model=model,
        model_name=args.model,
        language=args.language,
        device=args.device,
        compute_type=args.compute_type,
        overwrite=args.overwrite,
        print_segments=True,
    )

    if status == "processed":
        sys.exit(0)
    elif status == "skipped":
        sys.exit(0)
    else:  # failed
        sys.exit(1)


if __name__ == "__main__":
    main()
