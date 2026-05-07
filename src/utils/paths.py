"""
Path utilities for output directories and file naming.
"""

from pathlib import Path


def ensure_output_dirs() -> tuple[Path, Path]:
    """
    Create output directories if they don't exist.

    Returns:
        Tuple (transcripts_dir, markdown_dir)
    """
    transcripts_dir = Path("output/transcripts")
    markdown_dir = Path("output/markdown")
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    return transcripts_dir, markdown_dir


def get_output_paths(audio_path: Path) -> tuple[Path, Path]:
    """
    Generate output file paths for a given audio file.

    Args:
        audio_path: Path to the input audio file.

    Returns:
        Tuple (txt_path, md_path) where:
        - txt_path: output/transcripts/<audio_stem>.txt
        - md_path: output/markdown/<audio_stem>.md
    """
    stem = audio_path.stem
    transcripts_dir = Path("output/transcripts")
    markdown_dir = Path("output/markdown")
    txt_path = transcripts_dir / f"{stem}.txt"
    md_path = markdown_dir / f"{stem}.md"
    return txt_path, md_path
