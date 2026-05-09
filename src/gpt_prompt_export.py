#!/usr/bin/env python3
"""
Export ready-to-copy ChatGPT prompts from cleaned transcript files.
Stage 4.1-manual: manual fallback when OpenAI API quota is unavailable.
"""

import argparse
import sys
from pathlib import Path

try:
    from src.prompt_builder import build_summary_prompt
except ImportError:
    # Fallback for direct module execution
    from prompt_builder import build_summary_prompt


def validate_input_file(input_path: Path) -> None:
    """
    Validate that the input file exists and is a .txt file.

    Raises
    ------
    SystemExit with code 1 if validation fails.
    """
    if not input_path.is_file():
        print(
            f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".txt":
        print(
            f"Error: Input file must be a .txt file, got {input_path.suffix}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a ChatGPT prompt for manual summarization of a cleaned transcript.",
        epilog="Example: python -m src.gpt_prompt_export output/cleaned/test.txt --overwrite",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the cleaned transcript .txt file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/gpt_prompts"),
        help="Directory where the prompt markdown file will be saved (default: output/gpt_prompts)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing prompt file (default: skip if exists)",
    )
    args = parser.parse_args()

    # 1. Input validation
    validate_input_file(args.input_file)

    # 2. Prepare output path
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / f"{args.input_file.stem}_prompt.md"

    if output_file.exists() and not args.overwrite:
        print(
            f"Skip: Output file already exists {output_file}. Use --overwrite to replace.")
        sys.exit(0)

    # 3. Read transcript
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            transcript = f.read()
    except OSError as e:
        print(f"Error reading {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Build prompt
    prompt = build_summary_prompt(transcript, args.input_file.name)

    # 5. Save prompt to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(prompt)
    except OSError as e:
        print(f"Error writing {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 6. Console instructions
    print("=" * 50)
    print(f"ChatGPT prompt exported to: {output_file}")
    print()
    print("Next steps:")
    print("1. Copy the entire content of the prompt file.")
    print("2. Paste it into ChatGPT (web interface or app).")
    print("3. Copy ChatGPT's answer.")
    print(
        f"4. Save the answer manually to: output/gpt_summaries/{args.input_file.stem}.md")
    print("=" * 50)


if __name__ == "__main__":
    main()

