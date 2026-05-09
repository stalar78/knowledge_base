#!/usr/bin/env python3
"""
Course workflow status and next-step helper.

Stage 5.1 of GPT Course Knowledge Extractor.
Inspects a course workspace, counts files at each workflow stage,
and suggests the next step with a ready-to-run command.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def validate_course_workspace(courses_dir: Path, course_slug: str) -> Path:
    """
    Validate that the course workspace exists and contains course_config.json.

    Returns the course root path.
    Exits with error code 1 if validation fails.
    """
    course_root = courses_dir / course_slug
    if not course_root.is_dir():
        print(
            f"Error: Course workspace '{course_root}' does not exist.", file=sys.stderr)
        print(f"Create it first with:", file=sys.stderr)
        print(
            f"  python -m src.create_course_workspace {course_slug}", file=sys.stderr)
        sys.exit(1)

    config_path = course_root / "course_config.json"
    if not config_path.is_file():
        print(
            f"Error: Course configuration '{config_path}' not found.", file=sys.stderr)
        print(f"The workspace seems incomplete. Re-create it with:", file=sys.stderr)
        print(
            f"  python -m src.create_course_workspace {course_slug} --overwrite-readme", file=sys.stderr)
        sys.exit(1)

    return course_root


def load_course_config(course_root: Path, cli_slug: str) -> Dict[str, str]:
    """
    Load course_config.json and extract title and slug.

    Returns a dict with at least 'title' and 'slug' keys.
    """
    config_path = course_root / "course_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not read {config_path}: {e}", file=sys.stderr)
        config = {}

    title = config.get("title", cli_slug.replace(
        "_", " ").replace("-", " ").title())
    slug = config.get("course_slug", cli_slug)
    return {"title": title, "slug": slug}


def count_files_in_folder(folder: Path, patterns: List[str], exclude: List[str] = None) -> int:
    """
    Count files matching any of the glob patterns, excluding files in `exclude`.

    If folder does not exist, returns 0.
    """
    if not folder.is_dir():
        return 0

    count = 0
    exclude_set = set(exclude) if exclude else set()
    for pattern in patterns:
        for file in folder.glob(pattern):
            if file.is_file() and file.name not in exclude_set:
                count += 1
    return count


def get_counts(course_root: Path) -> Dict[str, int]:
    """
    Count generated/input files in each relevant subdirectory.

    Returns a dict with keys:
      - input_audio
      - input_video
      - raw_transcripts
      - transcript_markdown
      - cleaned_transcripts
      - cleaned_markdown
      - gpt_prompts
      - gpt_summaries
      - reports
    """
    # Supported media extensions (from src/utils/supported_formats.py)
    audio_exts = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma"]
    video_exts = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]

    audio_patterns = [f"*{ext}" for ext in audio_exts]
    video_patterns = [f"*{ext}" for ext in video_exts]

    # Exclude .gitkeep from all counts
    exclude = [".gitkeep"]

    counts = {
        "input_audio": count_files_in_folder(
            course_root / "input" / "audio", audio_patterns, exclude
        ),
        "input_video": count_files_in_folder(
            course_root / "input" / "video", video_patterns, exclude
        ),
        "raw_transcripts": count_files_in_folder(
            course_root / "output" / "transcripts", ["*.txt"], exclude
        ),
        "transcript_markdown": count_files_in_folder(
            course_root / "output" / "markdown", ["*.md"], exclude
        ),
        "cleaned_transcripts": count_files_in_folder(
            course_root / "output" / "cleaned", ["*.txt"], exclude
        ),
        "cleaned_markdown": count_files_in_folder(
            course_root / "output" / "cleaned_markdown", ["*.md"], exclude
        ),
        "gpt_prompts": count_files_in_folder(
            course_root / "output" / "gpt_prompts", ["*_prompt.md"], exclude
        ),
        "gpt_summaries": count_files_in_folder(
            course_root / "output" / "gpt_summaries", ["*.md"], exclude
        ),
        "reports": count_files_in_folder(
            course_root / "output" / "reports", ["*.md", "*.json"], exclude
        ),
    }
    return counts


def determine_next_step(counts: Dict[str, int], course_root: Path) -> Tuple[str, str]:
    """
    Determine the next suggested step and the command to run.

    Returns a tuple (step_description, command).
    """
    slug = course_root.name
    courses_dir = course_root.parent.name
    # Use relative path for readability
    rel_path = course_root.relative_to(
        Path.cwd()) if course_root.is_relative_to(Path.cwd()) else course_root

    total_input = counts["input_audio"] + counts["input_video"]

    if total_input == 0:
        step = "Add audio/video files"
        cmd = f"Place audio/video files into {rel_path}/input/audio/ or {rel_path}/input/video/"
        return step, cmd

    if counts["raw_transcripts"] == 0:
        step = "Transcribe course audio/video files"
        cmd = f"python -m src.transcribe_batch {rel_path}/input/audio --overwrite"
        return step, cmd

    if counts["cleaned_transcripts"] == 0:
        step = "Clean raw transcripts"
        cmd = (
            f"python -m src.cleanup_transcript {rel_path}/output/transcripts "
            f"--output-dir {rel_path}/output/cleaned "
            f"--markdown-output-dir {rel_path}/output/cleaned_markdown --overwrite"
        )
        return step, cmd

    if counts["gpt_prompts"] == 0:
        step = "Export manual ChatGPT prompts"
        cmd = (
            f"python -m src.gpt_prompt_batch_export {rel_path}/output/cleaned "
            f"--output-dir {rel_path}/output/gpt_prompts --overwrite"
        )
        return step, cmd

    if counts["gpt_summaries"] == 0:
        step = "Import manual ChatGPT summaries"
        cmd = (
            f"Use prompts from {rel_path}/output/gpt_prompts/, copy them into ChatGPT, "
            f"save answers locally, then import with:\n"
            f"python -m src.import_manual_summary manual_answer.md "
            f"--source-transcript {rel_path}/output/cleaned/<transcript>.txt "
            f"--output-dir {rel_path}/output/gpt_summaries --overwrite"
        )
        return step, cmd

    # Check if summary index files exist
    reports_dir = course_root / "output" / "reports"
    index_md = reports_dir / "summary_index.md"
    index_json = reports_dir / "summary_index.json"
    if not (index_md.is_file() and index_json.is_file()):
        step = "Build summary index"
        cmd = (
            f"python -m src.build_summary_index {rel_path}/output/gpt_summaries "
            f"--output {rel_path}/output/reports/summary_index.md "
            f"--json-output {rel_path}/output/reports/summary_index.json --overwrite"
        )
        return step, cmd

    step = "Course workspace is ready for course-level analysis"
    cmd = "No immediate command. Proceed to course-level analysis stage."
    return step, cmd


def print_status(
    title: str,
    slug: str,
    course_path: Path,
    counts: Dict[str, int],
    next_step: str,
    command: str,
) -> None:
    """
    Print a human-readable status report.
    """
    rel_path = course_path.relative_to(
        Path.cwd()) if course_path.is_relative_to(Path.cwd()) else course_path

    print("\n" + "=" * 60)
    print("Course Workflow Status")
    print("=" * 60)
    print(f"Course: {title}")
    print(f"Slug:   {slug}")
    print(f"Path:   {rel_path}")
    print()
    print("Files:")
    print(f"  Input audio:           {counts['input_audio']}")
    print(f"  Input video:           {counts['input_video']}")
    print(f"  Raw transcripts:       {counts['raw_transcripts']}")
    print(f"  Transcript markdown:   {counts['transcript_markdown']}")
    print(f"  Cleaned transcripts:   {counts['cleaned_transcripts']}")
    print(f"  Cleaned markdown:      {counts['cleaned_markdown']}")
    print(f"  GPT prompts:           {counts['gpt_prompts']}")
    print(f"  GPT summaries:         {counts['gpt_summaries']}")
    print(f"  Reports:               {counts['reports']}")
    print()
    print("Next suggested step:")
    print(f"  {next_step}")
    print()
    print("Suggested command:")
    for line in command.split("\n"):
        print(f"  {line}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect a course workspace and suggest the next workflow step.",
        epilog="Example: python -m src.course_workflow_status test_course",
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

    args = parser.parse_args()

    courses_dir = Path(args.courses_dir)
    if not courses_dir.is_dir():
        print(
            f"Error: Courses directory '{courses_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    course_root = validate_course_workspace(courses_dir, args.course_slug)
    config = load_course_config(course_root, args.course_slug)
    counts = get_counts(course_root)
    next_step, command = determine_next_step(counts, course_root)

    print_status(
        title=config["title"],
        slug=config["slug"],
        course_path=course_root,
        counts=counts,
        next_step=next_step,
        command=command,
    )


if __name__ == "__main__":
    main()

