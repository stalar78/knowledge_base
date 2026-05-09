#!/usr/bin/env python3
"""
Course‑aware path utilities.

Provides functions to locate and validate course workspace directories.
Used by course‑aware workflow wrappers (Stage 5.2).
"""

import sys
from pathlib import Path
from typing import Dict


def get_course_root(course_slug: str, courses_dir: Path = Path("courses")) -> Path:
    """
    Return the absolute path to the course workspace root.

    Does not validate existence.
    """
    return (courses_dir / course_slug).resolve()


def validate_course_root(course_root: Path) -> None:
    """
    Validate that the course workspace exists and contains course_config.json.

    If validation fails, prints an error and exits with code 1.
    """
    if not course_root.is_dir():
        print(
            f"Error: Course workspace '{course_root}' does not exist.",
            file=sys.stderr,
        )
        print(
            f"Create it first with:",
            file=sys.stderr,
        )
        print(
            f"  python -m src.create_course_workspace {course_root.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = course_root / "course_config.json"
    if not config_path.is_file():
        print(
            f"Error: Course configuration '{config_path}' not found.",
            file=sys.stderr,
        )
        print(
            f"The workspace seems incomplete. Re‑create it with:",
            file=sys.stderr,
        )
        print(
            f"  python -m src.create_course_workspace {course_root.name} --overwrite-readme",
            file=sys.stderr,
        )
        sys.exit(1)


def get_course_paths(
    course_slug: str, courses_dir: Path = Path("courses")
) -> Dict[str, Path]:
    """
    Return a dictionary of all important paths for a given course.

    The dictionary contains the following keys:
      - course_root
      - input_audio
      - input_video
      - output_transcripts
      - output_markdown
      - output_cleaned
      - output_cleaned_markdown
      - output_gpt_prompts
      - output_gpt_summaries
      - output_reports

    Validation is performed; if the course is invalid, the function exits.
    """
    course_root = get_course_root(course_slug, courses_dir)
    validate_course_root(course_root)

    return {
        "course_root": course_root,
        "input_audio": course_root / "input" / "audio",
        "input_video": course_root / "input" / "video",
        "output_transcripts": course_root / "output" / "transcripts",
        "output_markdown": course_root / "output" / "markdown",
        "output_cleaned": course_root / "output" / "cleaned",
        "output_cleaned_markdown": course_root / "output" / "cleaned_markdown",
        "output_gpt_prompts": course_root / "output" / "gpt_prompts",
        "output_gpt_summaries": course_root / "output" / "gpt_summaries",
        "output_reports": course_root / "output" / "reports",
    }


if __name__ == "__main__":
    # Simple test when run directly
    import argparse

    parser = argparse.ArgumentParser(
        description="Print course paths for a given slug."
    )
    parser.add_argument("course_slug", help="Course slug")
    parser.add_argument(
        "--courses-dir",
        default="courses",
        help="Directory containing course workspaces (default: 'courses')",
    )
    args = parser.parse_args()

    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    for key, path in paths.items():
        print(f"{key:30} {path}")
