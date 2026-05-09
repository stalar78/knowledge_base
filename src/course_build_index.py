#!/usr/bin/env python3
"""
Course-aware summary index builder wrapper.

Stage 5.2 of GPT Course Knowledge Extractor.
Builds a local index from imported GPT summary markdown files in a course's output/gpt_summaries folder,
writing index files to the course-specific reports directory.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.course_paths import get_course_paths
except ModuleNotFoundError:
    from course_paths import get_course_paths

try:
    from src.build_summary_index import (
        validate_directory,
        find_md_files,
        build_index_entry,
        write_markdown_index,
        write_json_index,
    )
except ModuleNotFoundError:
    from build_summary_index import (
        validate_directory,
        find_md_files,
        build_index_entry,
        write_markdown_index,
        write_json_index,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local index from imported GPT summary markdown files in a course.",
        epilog="Example: python -m src.course_build_index test_course --overwrite",
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
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for .md files recursively in subfolders.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing index files (default: skip if exists).",
    )

    args = parser.parse_args()

    # 1. Get course paths (validation happens inside)
    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    summaries_dir = paths["output_gpt_summaries"]
    reports_dir = paths["output_reports"]

    # 2. Check that summaries directory exists
    if not summaries_dir.is_dir():
        print(
            f"Info: Course GPT summaries directory '{summaries_dir}' does not exist.")
        print("      No summary files to index.")
        sys.exit(0)

    # 3. Validate directory (reuse existing validation)
    validate_directory(summaries_dir, "Summaries directory")

    # 4. Prepare output directory
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 5. Determine output file paths
    md_output = reports_dir / "summary_index.md"
    json_output = reports_dir / "summary_index.json"

    # 6. Check existing outputs (unless overwrite)
    if not args.overwrite and (md_output.exists() or json_output.exists()):
        print(f"Index files already exist in {reports_dir}.")
        print("Use --overwrite to regenerate.")
        sys.exit(0)

    # 7. Find .md files
    files = find_md_files(summaries_dir, args.recursive)
    if not files:
        print(
            f"No .md summary files found in '{summaries_dir}' (recursive={args.recursive}).")
        sys.exit(0)

    print(f"Found {len(files)} summary file(s) in course '{args.course_slug}'.")
    print(f"Index will be written to:")
    print(f"  Markdown: {md_output}")
    print(f"  JSON:     {json_output}")

    # 8. Build index entries
    entries = []
    for idx, file_path in enumerate(files, start=1):
        print(f"[{idx}/{len(files)}] Reading {file_path.name}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {file_path}: {e}", file=sys.stderr)
            continue
        entry = build_index_entry(file_path, content)
        entries.append(entry)

    if not entries:
        print("No valid summary files could be read.")
        sys.exit(1)

    # 9. Write indices
    try:
        write_markdown_index(entries, md_output)
        print(f"  Markdown index written to {md_output}")
    except Exception as e:
        print(f"  Error writing markdown index: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        write_json_index(entries, json_output)
        print(f"  JSON index written to {json_output}")
    except Exception as e:
        print(f"  Error writing JSON index: {e}", file=sys.stderr)
        sys.exit(1)

    # 10. Summary
    print("=" * 50)
    print("Course summary index built successfully.")
    print(f"  Processed: {len(entries)} summary file(s)")
    print(f"  Outputs:   {md_output.name}, {json_output.name}")
    sys.exit(0)


if __name__ == "__main__":
    main()

