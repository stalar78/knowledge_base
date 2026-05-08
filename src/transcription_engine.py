#!/usr/bin/env python3
"""
Shared transcription engine for GPT Course Knowledge Extractor.
Stage 2.1: extracted common logic from transcribe_audio.py and transcribe_batch.py.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.utils.paths import ensure_output_dirs, get_output_paths
    from src.utils.timestamps import format_timestamp
except ModuleNotFoundError:
    from utils.paths import ensure_output_dirs, get_output_paths
    from utils.timestamps import format_timestamp


def transcribe_file(
    audio_path: Path,
    model,
    model_name: str,
    language: str,
    device: str,
    compute_type: str,
    overwrite: bool = False,
    print_segments: bool = True,
) -> str:
    """
    Transcribe a single audio file using an already loaded WhisperModel.

    Returns:
        "processed" – transcription completed and files were written.
        "skipped"   – output files already exist and overwrite=False.
        "failed"    – transcription or file writing failed.
    """
    # 1. Ensure output directories exist
    ensure_output_dirs()

    # 2. Determine output paths
    txt_path, md_path = get_output_paths(audio_path)

    # 3. Check if outputs already exist (unless overwrite)
    if not overwrite and (txt_path.exists() or md_path.exists()):
        print(
            f"  Skipping {audio_path.name}: output already exists. Use --overwrite to regenerate.")
        return "skipped"

    print(f"  Transcribing '{audio_path.name}'...")
    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=language if language != "auto" else None,
            beam_size=5,
            vad_filter=True,
        )
    except Exception as e:
        print(f"  Transcription failed: {e}")
        return "failed"

    # Collect segments
    segment_list = []
    for seg in segments:
        start_fmt = format_timestamp(seg.start)
        end_fmt = format_timestamp(seg.end)
        line = f"[{start_fmt} - {end_fmt}] {seg.text.strip()}"
        segment_list.append((seg.start, seg.end, seg.text.strip(), line))
        if print_segments:
            print(line)

    # Write plain text transcript
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Transcript of: {audio_path.name}\n")
            f.write(f"Language: {info.language}\n")
            f.write(f"Duration: {info.duration:.2f} seconds\n")
            f.write("=" * 50 + "\n")
            for _, _, _, line in segment_list:
                f.write(line + "\n")
    except Exception as e:
        print(f"  Failed to write plain text transcript: {e}")
        return "failed"

    # Write markdown transcript
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Transcript: {audio_path.name}\n\n")
            f.write("## Metadata\n\n")
            f.write(f"- Source file: `{audio_path}`\n")
            f.write(f"- Language: `{info.language}`\n")
            f.write(f"- Duration: `{info.duration:.2f}` seconds\n")
            f.write(f"- Model: `{model_name}`\n")
            f.write(f"- Device: `{device}`\n")
            f.write(f"- Compute type: `{compute_type}`\n")
            f.write(
                f"- Detected language probability: `{info.language_probability:.2f}`\n\n")
            f.write("## Transcript\n\n")
            for _, _, text, line in segment_list:
                f.write(line + "\n\n")
    except Exception as e:
        print(f"  Failed to write markdown transcript: {e}")
        return "failed"

    print(f"    Saved: {txt_path.name}, {md_path.name}")
    return "processed"
