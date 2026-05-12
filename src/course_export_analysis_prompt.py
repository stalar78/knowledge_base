#!/usr/bin/env python3
"""
Course-aware manual export of a course-level analysis prompt.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from src.course_analysis_prompt import (
        build_course_analysis_prompt,
        discover_summary_files,
        read_text,
    )
    from src.course_paths import get_course_paths
except ModuleNotFoundError:
    from course_analysis_prompt import (
        build_course_analysis_prompt,
        discover_summary_files,
        read_text,
    )
    from course_paths import get_course_paths


def get_course_title(course_root: Path, fallback_slug: str) -> str:
    config_path = course_root / "course_config.json"
    if not config_path.is_file():
        return fallback_slug
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback_slug
    return config.get("title") or fallback_slug


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a manual ChatGPT prompt for course-level analysis.",
        epilog="Example: python -m src.course_export_analysis_prompt test_course --overwrite",
    )
    parser.add_argument("course_slug", help="Course identifier (slug) as used in courses/ directory.")
    parser.add_argument(
        "--courses-dir",
        default="courses",
        help="Directory containing course workspaces (default: 'courses').",
    )
    parser.add_argument("--recursive", action="store_true", help="Scan summary subfolders recursively.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing prompt file.")
    parser.add_argument(
        "--output-name",
        default="course_analysis_prompt.md",
        help="Output filename inside output/gpt_prompts (default: course_analysis_prompt.md).",
    )
    args = parser.parse_args()

    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    course_root = paths["course_root"]
    summary_index_path = paths["output_reports"] / "summary_index.md"
    summaries_dir = paths["output_gpt_summaries"]
    output_dir = paths["output_gpt_prompts"]
    output_path = output_dir / args.output_name

    if not summary_index_path.is_file():
        print(
            f"Error: summary index file not found: {summary_index_path}",
            file=sys.stderr,
        )
        print("Run summary index build first.", file=sys.stderr)
        sys.exit(1)

    if not summaries_dir.is_dir():
        print(
            f"Error: summaries directory not found: {summaries_dir}",
            file=sys.stderr,
        )
        print("Import manual GPT summaries first.", file=sys.stderr)
        sys.exit(1)

    summary_files = discover_summary_files(summaries_dir, recursive=args.recursive)
    if not summary_files:
        print(
            f"Error: no summary .md files found in: {summaries_dir}",
            file=sys.stderr,
        )
        print("Import manual GPT summaries first.", file=sys.stderr)
        sys.exit(1)

    if output_path.exists() and not args.overwrite:
        print(f"Skip: output file already exists: {output_path}")
        sys.exit(0)

    summary_index_text = read_text(summary_index_path)
    summaries = [(path, read_text(path)) for path in summary_files]
    course_title = get_course_title(course_root, args.course_slug)
    prompt_text = build_course_analysis_prompt(
        course_slug=args.course_slug,
        course_title=course_title,
        summary_index_text=summary_index_text,
        summaries=summaries,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding="utf-8")

    print("Course analysis prompt exported.")
    print(f"  summaries: {len(summary_files)}")
    print(f"  output: {output_path}")


if __name__ == "__main__":
    main()
