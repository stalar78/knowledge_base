#!/usr/bin/env python3
"""
Transcript cleanup script using a glossary replacement dictionary.
Stage 3 of GPT Course Knowledge Extractor.
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# No import needed; directories are created directly.


def load_replacements(glossary_path: Path) -> dict:
    """Load replacement dictionary from JSON file."""
    if not glossary_path.exists():
        print(f"Error: Glossary file '{glossary_path}' does not exist.")
        sys.exit(1)
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate that it's a dict of string -> string
        if not isinstance(data, dict):
            print(f"Error: Glossary must be a JSON object, got {type(data)}.")
            sys.exit(1)
        for k, v in data.items():
            if not isinstance(k, str) or not isinstance(v, str):
                print(f"Error: Non‑string key/value in glossary: {k} -> {v}")
                sys.exit(1)
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in glossary: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading glossary: {e}")
        sys.exit(1)


def apply_replacements(text: str, replacements: dict) -> tuple[str, int]:
    """
    Apply all replacements to the text.
    Returns (cleaned_text, replacement_count).
    """
    count = 0
    cleaned = text
    # Process replacements in order of decreasing key length to avoid overlapping issues
    for old, new in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
        if old in cleaned:
            # Simple replace (case‑sensitive)
            cleaned = cleaned.replace(old, new)
            # approximate; better to count before/after?
            count += cleaned.count(new)
    # More accurate counting: count occurrences before replacement
    # We'll implement a simple count per key
    count = 0
    cleaned = text
    for old, new in sorted(replacements.items(), key=lambda kv: -len(kv[0])):
        if old in cleaned:
            # Count occurrences
            occurrences = cleaned.count(old)
            cleaned = cleaned.replace(old, new)
            count += occurrences
    return cleaned, count


def clean_single_file(
    input_path: Path,
    replacements: dict,
    output_dir: Path,
    markdown_output_dir: Path,
    overwrite: bool,
    glossary_path: Path,
) -> tuple[str, int]:
    """
    Clean a single transcript file.
    Returns (status, replacement_count).
    status is "processed", "skipped", or "failed".
    replacement_count is zero for skipped/failed.
    """
    # Determine output paths
    stem = input_path.stem
    txt_out = output_dir / f"{stem}.txt"
    md_out = markdown_output_dir / f"{stem}.md"

    # Check existing outputs
    if not overwrite and (txt_out.exists() or md_out.exists()):
        print(
            f"  Skipping {input_path.name}: cleaned output already exists. Use --overwrite to regenerate.")
        return ("skipped", 0)

    # Read input
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            original = f.read()
    except Exception as e:
        print(f"  Failed to read {input_path}: {e}")
        return ("failed", 0)

    # Apply replacements
    cleaned, count = apply_replacements(original, replacements)

    # Write cleaned plain text
    try:
        with open(txt_out, "w", encoding="utf-8") as f:
            f.write(cleaned)
    except Exception as e:
        print(f"  Failed to write cleaned text to {txt_out}: {e}")
        return ("failed", 0)

    # Write cleaned markdown
    try:
        with open(md_out, "w", encoding="utf-8") as f:
            f.write(f"# Cleaned Transcript: {input_path.name}\n\n")
            f.write("## Metadata\n\n")
            f.write(f"- Source transcript: `{input_path}`\n")
            f.write(f"- Glossary: `{glossary_path}`\n")
            f.write(f"- Replacements applied: {count}\n\n")
            f.write("## Cleaned Transcript\n\n")
            f.write(cleaned)
    except Exception as e:
        print(f"  Failed to write cleaned markdown to {md_out}: {e}")
        return ("failed", 0)

    print(f"  Processed {input_path.name}: {count} replacement(s)")
    return ("processed", count)


def main():
    parser = argparse.ArgumentParser(
        description="Clean transcript files using a glossary replacement dictionary."
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to a single .txt transcript file or a folder containing .txt files",
    )
    parser.add_argument(
        "--glossary",
        default="config/glossary_replacements.json",
        help="Path to JSON glossary file (default: config/glossary_replacements.json)",
    )
    parser.add_argument(
        "--output-dir",
        default="output/cleaned",
        help="Directory for cleaned plain‑text transcripts (default: output/cleaned)",
    )
    parser.add_argument(
        "--markdown-output-dir",
        default="output/cleaned_markdown",
        help="Directory for cleaned markdown transcripts (default: output/cleaned_markdown)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders recursively (only when input is a folder)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing cleaned output files",
    )

    args = parser.parse_args()

    # Convert paths
    input_path = Path(args.input_path).resolve()
    glossary_path = Path(args.glossary).resolve()
    output_dir = Path(args.output_dir).resolve()
    markdown_output_dir = Path(args.markdown_output_dir).resolve()

    # Validate input path
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.")
        sys.exit(1)

    # Load replacements
    replacements = load_replacements(glossary_path)
    print(f"Loaded {len(replacements)} replacement(s) from {glossary_path}")

    # Ensure output directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_output_dir.mkdir(parents=True, exist_ok=True)

    # Collect .txt files to process
    files_to_process = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".txt":
            files_to_process = [input_path]
        else:
            print(
                f"Error: Input file must have .txt extension, got '{input_path.suffix}'.")
            sys.exit(1)
    else:
        # Directory
        pattern = "**/*.txt" if args.recursive else "*.txt"
        files_to_process = list(input_path.glob(pattern))
        # Filter out directories (just in case)
        files_to_process = [f for f in files_to_process if f.is_file()]
        files_to_process.sort(key=lambda p: str(p).lower())

    if not files_to_process:
        print(f"No .txt files found in '{input_path}'.")
        sys.exit(0)

    print(f"Found {len(files_to_process)} .txt file(s) to process.")

    # Process each file
    processed = 0
    skipped = 0
    failed = 0
    total_replacements = 0

    for idx, file_path in enumerate(files_to_process, start=1):
        print(f"[{idx}/{len(files_to_process)}] {file_path.name}")
        status, replacement_count = clean_single_file(
            file_path,
            replacements,
            output_dir,
            markdown_output_dir,
            args.overwrite,
            glossary_path,
        )
        if status == "processed":
            processed += 1
            total_replacements += replacement_count
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1
        print()  # empty line for readability

    # Final summary
    print("=" * 50)
    print("Transcript cleanup completed.")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total replacements: {total_replacements}")
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
