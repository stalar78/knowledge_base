#!/usr/bin/env python3
"""
Course‑aware ChatGPT prompt export wrapper.

Stage 5.2 of GPT Course Knowledge Extractor.
Exports ready‑to‑copy ChatGPT prompts from cleaned transcript files in a course's output/cleaned folder,
writing prompts to the course‑specific gpt_prompts directory.
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
    from src.gpt_prompt_batch_export import (
        validate_input_folder,
        find_txt_files,
        export_prompt_for_file,
    )
except ModuleNotFoundError:
    from gpt_prompt_batch_export import (
        validate_input_folder,
        find_txt_files,
        export_prompt_for_file,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export ChatGPT prompts for cleaned transcripts in a course.",
        epilog="Example: python -m src.course_export_prompts test_course --overwrite",
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
        help="Search for .txt files recursively in subfolders.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing prompt files (default: skip if exists).",
    )

    args = parser.parse_args()

    # 1. Get course paths (validation happens inside)
    paths = get_course_paths(args.course_slug, Path(args.courses_dir))
    input_dir = paths["output_cleaned"]
    output_dir = paths["output_gpt_prompts"]

    # 2. Check that input directory exists
    if not input_dir.is_dir():
        print(
            f"Info: Course cleaned transcripts directory '{input_dir}' does not exist.")
        print("      No cleaned transcript files to export prompts from.")
        sys.exit(0)

    # 3. Validate input folder (reuse existing validation)
    validate_input_folder(input_dir)

    # 4. Prepare output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # 5. Find .txt files
    files = find_txt_files(input_dir, args.recursive)
    if not files:
        print(
            f"No .txt files found in '{input_dir}' (recursive={args.recursive}).")
        sys.exit(0)

    print(
        f"Found {len(files)} cleaned transcript file(s) in course '{args.course_slug}'.")
    print(f"Prompts will be written to: {output_dir}")

    # 6. Process each file
    exported = 0
    skipped = 0
    failed = 0

    for idx, input_file in enumerate(files, start=1):
        exported_flag, skipped_flag = export_prompt_for_file(
            input_file=input_file,
            output_dir=output_dir,
            overwrite=args.overwrite,
            index=idx,
            total=len(files),
        )
        if exported_flag:
            exported += 1
        elif skipped_flag:
            skipped += 1
        else:
            failed += 1

    # 7. Summary
    print("=" * 50)
    print("Course prompt export completed.")
    print(f"  Exported: {exported} file(s)")
    print(f"  Skipped:  {skipped} file(s)")
    print(f"  Failed:   {failed} file(s)")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
