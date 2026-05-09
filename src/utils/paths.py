"""
Path utilities for output directories and file naming.
"""

from pathlib import Path


def ensure_output_dirs(
    transcripts_dir: Path = None, markdown_dir: Path = None
) -> tuple[Path, Path]:
    """
    Create output directories if they don't exist.

    Args:
        transcripts_dir: Optional custom directory for .txt transcripts.
        markdown_dir: Optional custom directory for .md transcripts.

    Returns:
        Tuple (transcripts_dir, markdown_dir)
    """
    if transcripts_dir is None:
        transcripts_dir = Path("output/transcripts")
    if markdown_dir is None:
        markdown_dir = Path("output/markdown")
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    return transcripts_dir, markdown_dir


def get_output_paths(
    audio_path: Path, transcripts_dir: Path = None, markdown_dir: Path = None
) -> tuple[Path, Path]:
    """
    Generate output file paths for a given audio file.

    Args:
        audio_path: Path to the input audio file.
        transcripts_dir: Optional custom directory for .txt transcripts.
        markdown_dir: Optional custom directory for .md transcripts.

    Returns:
        Tuple (txt_path, md_path) where:
        - txt_path: transcripts_dir/<audio_stem>.txt
        - md_path: markdown_dir/<audio_stem>.md
    """
    stem = audio_path.stem
    if transcripts_dir is None:
        transcripts_dir = Path("output/transcripts")
    if markdown_dir is None:
        markdown_dir = Path("output/markdown")
    txt_path = transcripts_dir / f"{stem}.txt"
    md_path = markdown_dir / f"{stem}.md"
    return txt_path, md_path
