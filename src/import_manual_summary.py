#!/usr/bin/env python3
"""
Manual ChatGPT summary import.

Stage 4.3 of GPT Course Knowledge Extractor.
Imports a manually obtained ChatGPT answer and saves it as a standardized
markdown summary with metadata.

Usage:
    python -m src.import_manual_summary answer.md --source-transcript cleaned.txt
    python src/import_manual_summary.py answer.md --source-transcript cleaned.txt --overwrite
"""

import argparse
import sys
from pathlib import Path


def validate_file(path: Path, expected_suffix, description: str) -> None:
    """Check that a file exists and has one of the expected extensions.

    expected_suffix can be a single string (e.g., '.txt') or a list/tuple of strings.
    """
    if not path.exists():
        print(f"Error: {description} does not exist: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"Error: {description} is not a file: {path}", file=sys.stderr)
        sys.exit(1)

    if isinstance(expected_suffix, str):
        allowed = [expected_suffix]
    else:
        allowed = list(expected_suffix)

    if path.suffix.lower() not in allowed:
        if len(allowed) == 1:
            msg = f"must have extension {allowed[0]}"
        else:
            msg = f"must have one of the extensions {', '.join(allowed)}"
        print(
            f"Error: {description} {msg}: {path}",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a manually obtained ChatGPT answer as a summary.",
        epilog="Example: python -m src.import_manual_summary manual_answer.md "
               "--source-transcript output/cleaned/test.txt --overwrite",
    )
    parser.add_argument(
        "answer_file",
        type=Path,
        help="Path to the markdown or text file containing ChatGPT's answer (.md or .txt)",
    )
    parser.add_argument(
        "--source-transcript",
        required=True,
        type=Path,
        help="Path to the original cleaned transcript .txt file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/gpt_summaries"),
        help="Directory where the imported summary will be saved (default: output/gpt_summaries)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing summary file (default: skip if exists)",
    )

    args = parser.parse_args()

    # 1. Validate input files
    validate_file(args.answer_file, [".md", ".txt"], "Answer file")
    validate_file(args.source_transcript, ".txt", "Source transcript file")

    # 2. Determine output path
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / f"{args.source_transcript.stem}.md"

    # 3. Skip if output exists and --overwrite not given
    if output_file.exists() and not args.overwrite:
        print(
            f"Skipping import: summary already exists at {output_file}. "
            "Use --overwrite to regenerate."
        )
        sys.exit(0)

    # 4. Read answer content
    try:
        with open(args.answer_file, "r", encoding="utf-8") as f:
            answer_content = f.read()
    except Exception as e:
        print(f"Error reading answer file: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Build standardized markdown
    metadata = f"""# GPT Summary: {args.source_transcript.name}

## Metadata

- Source transcript: {args.source_transcript.resolve()}
- Manual answer file: {args.answer_file.resolve()}
- Import mode: manual ChatGPT
- Notes: Imported from a manually copied ChatGPT answer.

---

"""
    full_content = metadata + answer_content

    # 6. Write output
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_content)
    except Exception as e:
        print(f"Error writing summary file: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. Print success message
    print("Imported manual summary:")
    print(f"  Source transcript: {args.source_transcript}")
    print(f"  Answer file:       {args.answer_file}")
    print(f"  Output:            {output_file}")


if __name__ == "__main__":
    main()
