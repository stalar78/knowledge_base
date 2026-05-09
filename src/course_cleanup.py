#!/usr/bin/env python3
"""
Course-aware transcript cleanup wrapper.

Stage 5.2 of GPT Course Knowledge Extractor.
Cleans raw transcript files in a course's output/transcripts folder,
writing cleaned outputs to the course-specific cleaned directories.
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
    from src.cleanup_transcript import (
        load_replacements,
        clean_single_file,
    )
except ModuleNotFoundError:
    from cleanup_transcript import (
        load_replacements,
        clean_single_file,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean raw transcript files in a course's output/transcripts folder.",
        epilog="Example: python -m src.course_cleanup test_course --overwrite",
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
        "--glossary",
        default="config/glossary_replacements.json",
        help="Path to JSON glossary file (default: config/glossary_replacements.json)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders of output/transcripts recursively.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing cleaned output files.",
    )

    args = parser.parse_args()

    # 1. Get course paths (validation happens inside)
    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    input_dir = paths["output_transcripts"]
    output_dir = paths["output_cleaned"]
    markdown_output_dir = paths["output_cleaned_markdown"]

    # 2. Check that input directory exists
    if not input_dir.is_dir():
        print(
            f"Info: Course raw transcripts directory '{input_dir}' does not exist.")
        print("      No transcript files to clean.")
        sys.exit(0)

    # 3. Load replacements
    glossary_path = Path(args.glossary).resolve()
    replacements = load_replacements(glossary_path)
    print(f"Loaded {len(replacements)} replacement(s) from {glossary_path}")

    # 4. Ensure output directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_output_dir.mkdir(parents=True, exist_ok=True)

    # 5. Collect .txt files to process
    pattern = "**/*.txt" if args.recursive else "*.txt"
    files_to_process = list(input_dir.glob(pattern))
    files_to_process = [f for f in files_to_process if f.is_file()]
    files_to_process.sort(key=lambda p: str(p).lower())

    if not files_to_process:
        print(f"No .txt transcript files found in '{input_dir}'.")
        sys.exit(0)

    print(
        f"Found {len(files_to_process)} transcript file(s) in course '{args.course_slug}'.")
    print(f"Cleaned outputs will be written to:")
    print(f"  TXT: {output_dir}")
    print(f"  MD:  {markdown_output_dir}")

    # 6. Process each file
    processed = 0
    skipped = 0
    failed = 0
    total_replacements = 0

    for idx, input_path in enumerate(files_to_process, start=1):
        print(f"[{idx}/{len(files_to_process)}] {input_path.name}")
        status, count, _ = clean_single_file(
            input_path=input_path,
            replacements=replacements,
            output_dir=output_dir,
            markdown_output_dir=markdown_output_dir,
            overwrite=args.overwrite,
            glossary_path=glossary_path,
        )
        if status == "processed":
            processed += 1
            total_replacements += count
        elif status == "skipped":
            skipped += 1
        else:  # failed
            failed += 1
        print()  # empty line for readability

    # 7. Summary
    print("=" * 50)
    print("Course transcript cleanup completed.")
    print(f"  Processed: {processed} file(s)")
    print(f"  Skipped:   {skipped} file(s)")
    print(f"  Failed:    {failed} file(s)")
    if processed > 0:
        print(f"  Total replacements applied: {total_replacements}")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

