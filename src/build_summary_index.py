#!/usr/bin/env python3
"""
Build a local summary index from imported GPT summary markdown files.

Stage 4.4 of GPT Course Knowledge Extractor.
Scans a directory for .md summary files, extracts metadata,
and generates a markdown and JSON index.

Usage:
    python -m src.build_summary_index output/gpt_summaries --overwrite
    python src/build_summary_index.py output/gpt_summaries --overwrite
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any


def validate_directory(path: Path, description: str) -> None:
    """Check that a directory exists and is a directory."""
    if not path.exists():
        print(f"Error: {description} does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_dir():
        print(f"Error: {description} is not a directory: {path}",
              file=sys.stderr)
        sys.exit(1)


def find_md_files(directory: Path, recursive: bool) -> List[Path]:
    """Return sorted list of .md files in directory."""
    pattern = "**/*.md" if recursive else "*.md"
    files = list(directory.glob(pattern))
    # Exclude directories (should not happen with .md pattern)
    files = [f for f in files if f.is_file()]
    files.sort(key=lambda p: p.as_posix())
    return files


def extract_metadata(content: str) -> Dict[str, str]:
    """
    Extract metadata from summary markdown content.

    Expected format:
    # GPT Summary: <title>
    ## Metadata
    - Source transcript: ...
    - Manual answer file: ...
    - Import mode: ...
    - Notes: ...
    """
    metadata = {
        "title": "",
        "source_transcript": "",
        "manual_answer_file": "",
        "import_mode": "",
    }

    lines = content.splitlines()
    # Extract title from first H1 line
    for line in lines:
        if line.startswith("# "):
            metadata["title"] = line[2:].strip()
            break

    # Look for metadata section
    in_metadata = False
    for line in lines:
        if line.strip() == "## Metadata":
            in_metadata = True
            continue
        if in_metadata and line.strip().startswith("##"):
            # Next section, stop
            break
        if in_metadata and line.strip().startswith("- "):
            # Parse key-value
            parts = line.strip()[2:].split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower().replace(" ", "_")
                value = parts[1].strip()
                if key in metadata:
                    metadata[key] = value
                elif key == "source_transcript":
                    metadata["source_transcript"] = value
                elif key == "manual_answer_file":
                    metadata["manual_answer_file"] = value
                elif key == "import_mode":
                    metadata["import_mode"] = value

    return metadata


def count_words(text: str) -> int:
    """Approximate word count (split on whitespace)."""
    return len(text.split())


def build_index_entry(file_path: Path, content: str) -> Dict[str, Any]:
    """Create a dictionary with all data for one summary file."""
    metadata = extract_metadata(content)
    return {
        "summary_file": file_path.as_posix(),
        "title": metadata["title"],
        "source_transcript": metadata["source_transcript"],
        "manual_answer_file": metadata["manual_answer_file"],
        "import_mode": metadata["import_mode"],
        "word_count": count_words(content),
    }


def write_markdown_index(entries: List[Dict[str, Any]], output_path: Path) -> None:
    """Write markdown index table."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Summary Index\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Summary files: {len(entries)}\n\n")
        f.write("## Files\n\n")
        f.write("| # | Summary file | Title | Source transcript | Words |\n")
        f.write("|---:|:---|:---|:---|:---:|\n")
        for i, entry in enumerate(entries, start=1):
            f.write(
                f"| {i} | {entry['summary_file']} | {entry['title']} | "
                f"{entry['source_transcript']} | {entry['word_count']} |\n"
            )
        f.write("\n## Notes\n\n")
        f.write("This index is generated locally and does not call the OpenAI API.\n")


def write_json_index(entries: List[Dict[str, Any]], output_path: Path) -> None:
    """Write JSON index."""
    data = {
        "summary_count": len(entries),
        "files": entries,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a local index from imported GPT summary markdown files.",
        epilog="Example: python -m src.build_summary_index output/gpt_summaries --overwrite",
    )
    parser.add_argument(
        "summaries_dir",
        type=Path,
        help="Path to folder with .md summary files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/reports/summary_index.md"),
        help="Markdown output file (default: output/reports/summary_index.md)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("output/reports/summary_index.json"),
        help="JSON output file (default: output/reports/summary_index.json)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for .md files recursively in subfolders",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files (default: skip if exists)",
    )

    args = parser.parse_args()

    # 1. Validate input directory
    validate_directory(args.summaries_dir, "Summaries directory")

    # 2. Find .md files
    md_files = find_md_files(args.summaries_dir, args.recursive)
    if not md_files:
        print(f"No .md files found in {args.summaries_dir}")
        sys.exit(0)

    # 3. Ensure output parent directories exist
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)

    # 4. Skip if outputs exist and --overwrite not given
    if not args.overwrite:
        skip = False
        if args.output.exists():
            print(f"Skipping: markdown index already exists at {args.output}")
            skip = True
        if args.json_output.exists():
            print(f"Skipping: JSON index already exists at {args.json_output}")
            skip = True
        if skip:
            sys.exit(0)

    # 5. Process each file
    entries = []
    for file_path in md_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: could not read {file_path}: {e}", file=sys.stderr)
            continue
        entry = build_index_entry(file_path, content)
        entries.append(entry)

    # 6. Write outputs
    try:
        write_markdown_index(entries, args.output)
        write_json_index(entries, args.json_output)
    except Exception as e:
        print(f"Error writing index files: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. Success message
    print(f"Index built successfully.")
    print(f"  Markdown: {args.output}")
    print(f"  JSON:     {args.json_output}")
    print(f"  Summaries indexed: {len(entries)}")


if __name__ == "__main__":
    main()
