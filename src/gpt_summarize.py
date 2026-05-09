#!/usr/bin/env python3
"""
GPT‑based summarization for a single cleaned transcript file.
Stage 4.1 of the GPT Course Knowledge Extractor.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

try:
    from src.gpt_client import get_openai_client_and_settings
except ImportError:
    # Fallback for direct module execution
    from gpt_client import get_openai_client_and_settings

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
        description="Generate a GPT‑based summary of a cleaned transcript file.",
        epilog="Example: python -m src.gpt_summarize output/cleaned/test.txt --overwrite",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the cleaned transcript .txt file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/gpt_summaries"),
        help="Directory where the summary markdown file will be saved (default: output/gpt_summaries)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing summary file (default: skip if exists)",
    )
    args = parser.parse_args()

    # 1. Input validation
    validate_input_file(args.input_file)

    # 2. Prepare output path
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_file = args.output_dir / f"{args.input_file.stem}.md"

    if output_file.exists() and not args.overwrite:
        print(
            f"Skip: Output file already exists {output_file}. Use --overwrite to replace.")
        sys.exit(0)

    # 3. Load OpenAI client and settings
    try:
        client, settings = get_openai_client_and_settings()
    except Exception as e:
        print(f"Error loading OpenAI configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Read transcript
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            transcript = f.read()
    except OSError as e:
        print(f"Error reading {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Build prompt
    prompt = build_summary_prompt(transcript, args.input_file.name)

    # 6. Call OpenAI API
    print(f"Calling OpenAI API with model {settings['model']}...")
    try:
        response = client.responses.create(
            model=settings["model"],
            input=prompt,
            temperature=settings.get("temperature", 0.2),
            max_output_tokens=settings.get("max_output_tokens", 2000),
        )
    except Exception as e:
        print(f"OpenAI API error: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. Extract response text
    if not hasattr(response, "output_text") or not response.output_text:
        print("Error: No output text in API response.", file=sys.stderr)
        sys.exit(1)

    gpt_output = response.output_text

    # 8. Build final markdown with metadata
    metadata = f"""# GPT Summary: {args.input_file.name}

## Metadata

- Source file: {args.input_file.resolve()}
- Model: {settings['model']}
- Temperature: {settings.get('temperature', 'unknown')}
- Max output tokens: {settings.get('max_output_tokens', 'unknown')}

---

"""
    final_content = metadata + gpt_output

    # 9. Save to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_content)
    except OSError as e:
        print(f"Error writing {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # 10. Console success message
    print("=" * 50)
    print("GPT summary generated successfully.")
    print(f"  Input:  {args.input_file}")
    print(f"  Output: {output_file}")
    print(f"  Model:  {settings['model']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
