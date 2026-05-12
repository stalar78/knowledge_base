#!/usr/bin/env python3
"""
Course-aware wrapper for Obsidian vault export.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from src.course_paths import get_course_paths
    from src.obsidian_exporter import discover_markdown_files, export_course_to_obsidian
except ModuleNotFoundError:
    from course_paths import get_course_paths
    from obsidian_exporter import discover_markdown_files, export_course_to_obsidian


def get_course_title(course_root: Path, fallback_slug: str) -> str:
    config_path = course_root / "course_config.json"
    if not config_path.is_file():
        return fallback_slug
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback_slug
    return data.get("title") or fallback_slug


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a course workspace into an Obsidian-ready structure.",
        epilog="Example: python -m src.course_export_obsidian test_course --overwrite",
    )
    parser.add_argument("course_slug", help="Course identifier (slug) as used in courses/ directory.")
    parser.add_argument(
        "--courses-dir",
        default="courses",
        help="Directory containing course workspaces (default: 'courses').",
    )
    parser.add_argument("--recursive", action="store_true", help="Scan summaries recursively.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing exported files.")
    parser.add_argument(
        "--output-dir",
        default="",
        help="Optional custom output directory. Defaults to courses/<slug>/output/obsidian_export.",
    )
    args = parser.parse_args()

    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    course_root = paths["course_root"]
    reports_dir = paths["output_reports"]
    summaries_dir = paths["output_gpt_summaries"]
    prompts_dir = paths["output_gpt_prompts"]

    summary_index_path = reports_dir / "summary_index.md"
    analysis_prompt_path = prompts_dir / "course_analysis_prompt.md"

    if not summary_index_path.is_file():
        print(f"Error: summary index file not found: {summary_index_path}", file=sys.stderr)
        print("Run summary index build first.", file=sys.stderr)
        sys.exit(1)

    if not summaries_dir.is_dir():
        print(f"Error: summaries directory not found: {summaries_dir}", file=sys.stderr)
        print("Import manual GPT summaries first.", file=sys.stderr)
        sys.exit(1)

    summary_files = discover_markdown_files(summaries_dir, recursive=args.recursive)
    if not summary_files:
        print(f"Error: no summary .md files found in: {summaries_dir}", file=sys.stderr)
        print("Import manual GPT summaries first.", file=sys.stderr)
        sys.exit(1)

    if not analysis_prompt_path.is_file():
        print(
            f"Warning: course analysis prompt not found: {analysis_prompt_path}\n"
            "         Export will continue with placeholder prompt note."
        )
        analysis_prompt_input = None
    else:
        analysis_prompt_input = analysis_prompt_path

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = course_root / "output" / "obsidian_export"

    course_title = get_course_title(course_root, args.course_slug)
    result = export_course_to_obsidian(
        course_slug=args.course_slug,
        course_title=course_title,
        summary_index_path=summary_index_path,
        summary_files=summary_files,
        analysis_prompt_path=analysis_prompt_input,
        output_dir=output_dir,
        overwrite=args.overwrite,
        recursive=args.recursive,
    )

    print("Obsidian export completed.")
    print(f"  summaries: {result['summaries']}")
    print(f"  written: {result['written']}")
    print(f"  skipped: {result['skipped']}")
    print(f"  output: {result['output_dir']}")


if __name__ == "__main__":
    main()
