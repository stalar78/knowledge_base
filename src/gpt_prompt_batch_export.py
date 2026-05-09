#!/usr/bin/env python3
"""
Batch export of ready-to-copy ChatGPT prompts from cleaned transcript files.
Stage 4.2 of the GPT Course Knowledge Extractor.
"""

import argparse
import sys
from pathlib import Path

try:
    from src.prompt_builder import build_summary_prompt
except ImportError:
    # Fallback for direct module execution
    from prompt_builder import build_summary_prompt


def validate_input_folder(input_path: Path) -> None:
    """
    Validate that the input path exists and is a directory.

    Raises
    ------
    SystemExit with code 1 if validation fails.
    """
    if not input_path.exists():
        print(
            f"Error: Input folder does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.is_dir():
        print(
            f"Error: Input path is not a directory: {input_path}", file=sys.stderr)
        sys.exit(1)


def find_txt_files(folder: Path, recursive: bool) -> list[Path]:
    """
    Find all .txt files in the folder.

    Parameters
    ----------
    folder : Path
        Root directory to search.
    recursive : bool
        If True, search recursively in subdirectories.

    Returns
    -------
    list[Path]
        Sorted list of .txt file paths.
    """
    pattern = "**/*.txt" if recursive else "*.txt"
    files = list(folder.glob(pattern))
    # Exclude directories (though glob shouldn't return them)
    files = [f for f in files if f.is_file()]
    files.sort(key=lambda p: p.as_posix())
    return files


def export_prompt_for_file(
    input_file: Path,
    output_dir: Path,
    overwrite: bool,
    index: int,
    total: int,
) -> tuple[bool, bool]:
    """
    Export a ChatGPT prompt for a single transcript file.

    Parameters
    ----------
    input_file : Path
        Path to the cleaned transcript .txt file.
    output_dir : Path
        Directory where the prompt markdown file will be saved.
    overwrite : bool
        If True, overwrite existing prompt file.
    index : int
        Current file index (for progress display).
    total : int
        Total number of files.

    Returns
    -------
    tuple (exported, skipped)
        exported: True if a new prompt was written.
        skipped: True if the prompt already existed and was skipped.
    """
    output_file = output_dir / f"{input_file.stem}_prompt.md"

    if output_file.exists() and not overwrite:
        print(
            f"  Skipping {input_file.name}: prompt already exists. Use --overwrite to regenerate.")
        return False, True

    # Read transcript
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            transcript = f.read()
    except OSError as e:
        print(f"  Error reading {input_file}: {e}", file=sys.stderr)
        return False, False

    # Build prompt
    prompt = build_summary_prompt(transcript, input_file.name)

    # Write prompt
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prompt)
    except OSError as e:
        print(f"  Error writing {output_file}: {e}", file=sys.stderr)
        return False, False

    print(f"  [{index}/{total}] Exported prompt for {input_file.name}")
    return True, False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch export ChatGPT prompts for manual summarization of cleaned transcripts.",
        epilog="Example: python -m src.gpt_prompt_batch_export output/cleaned --overwrite",
    )
    parser.add_argument(
        "input_folder",
        type=Path,
        help="Path to the folder containing cleaned transcript .txt files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/gpt_prompts"),
        help="Directory where prompt markdown files will be saved (default: output/gpt_prompts)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for .txt files recursively in subfolders",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing prompt files (default: skip if exists)",
    )
    args = parser.parse_args()

    # 1. Input validation
    validate_input_folder(args.input_folder)

    # 2. Prepare output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Find .txt files
    files = find_txt_files(args.input_folder, args.recursive)
    if not files:
        print(
            f"No .txt files found in {args.input_folder} (recursive={args.recursive}).")
        sys.exit(0)

    print(f"Found {len(files)} transcript file(s).")
    if args.recursive:
        print("(searching recursively)")

    # 4. Process each file
    exported_count = 0
    skipped_count = 0
    failed_count = 0

    for i, file in enumerate(files, start=1):
        exported, skipped = export_prompt_for_file(
            file, args.output_dir, args.overwrite, i, len(files)
        )
        if exported:
            exported_count += 1
        elif skipped:
            skipped_count += 1
        else:
            failed_count += 1

    # 5. Final summary
    print("\n" + "=" * 50)
    print("Batch prompt export completed.")
    print(f"  Exported: {exported_count}")
    print(f"  Skipped:  {skipped_count}")
    print(f"  Failed:   {failed_count}")
    print(f"  Total:    {len(files)}")
    print()
    print(f"Prompts saved in: {args.output_dir.resolve()}")
    print("=" * 50)


if __name__ == "__main__":
    main()

