#!/usr/bin/env python3
"""
Course workspace initializer.

Stage 5.0 of GPT Course Knowledge Extractor.
Creates a folder structure for a new course under courses/<course_slug>/.

Usage:
    python -m src.create_course_workspace python_backend_course --title "Python Backend Course"
    python src/create_course_workspace.py python_backend_course --overwrite-readme
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


def validate_slug(slug: str) -> bool:
    """Check that slug contains only lowercase letters, numbers, hyphens, underscores."""
    return bool(re.fullmatch(r"[a-z0-9\-_]+", slug))


def create_folder(path: Path, description: str) -> None:
    """Create directory if it doesn't exist, print message."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  Created {description}: {path}")
    else:
        print(f"  {description} already exists: {path}")


def add_gitkeep(path: Path) -> None:
    """Create .gitkeep file in directory if it doesn't exist."""
    gitkeep = path / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        print(f"    Added .gitkeep to {path.name}/")


def create_course_structure(course_root: Path) -> None:
    """Create all subdirectories and .gitkeep files."""
    folders = [
        ("input/audio", "Input audio folder"),
        ("input/video", "Input video folder"),
        ("output/transcripts", "Output transcripts folder"),
        ("output/markdown", "Output markdown folder"),
        ("output/cleaned", "Output cleaned transcripts folder"),
        ("output/cleaned_markdown", "Output cleaned markdown folder"),
        ("output/gpt_prompts", "Output GPT prompts folder"),
        ("output/gpt_summaries", "Output GPT summaries folder"),
        ("output/reports", "Output reports folder"),
    ]
    for rel_path, desc in folders:
        folder = course_root / rel_path
        create_folder(folder, desc)
        add_gitkeep(folder)


def create_course_config(course_root: Path, slug: str, title: str) -> None:
    """Create course_config.json if it doesn't exist."""
    config_path = course_root / "course_config.json"
    if config_path.exists():
        print(f"  Course config already exists: {config_path}")
        return

    config = {
        "course_slug": slug,
        "title": title,
        "created_by": "GPT Course Knowledge Extractor",
        "workflow": [
            "transcription",
            "cleanup",
            "manual_prompt_export",
            "manual_summary_import",
            "summary_index",
        ],
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"  Created course config: {config_path}")


def create_course_readme(course_root: Path, slug: str, title: str, overwrite: bool) -> None:
    """Create README.md with example commands."""
    readme_path = course_root / "README.md"
    if readme_path.exists() and not overwrite:
        print(
            f"  Course README already exists: {readme_path} (use --overwrite-readme to regenerate)")
        return

    commands = f"""# {title}

This folder contains materials for the course **{title}** (`{slug}`).

## Folder structure

- `input/audio/` – place audio files for transcription.
- `input/video/` – place video files (audio will be extracted).
- `output/transcripts/` – raw transcript files.
- `output/markdown/` – formatted transcripts with metadata.
- `output/cleaned/` – cleaned transcript text files.
- `output/cleaned_markdown/` – cleaned transcripts in markdown format.
- `output/gpt_prompts/` – ready‑to‑copy ChatGPT prompts.
- `output/gpt_summaries/` – imported ChatGPT summaries.
- `output/reports/` – audit reports and summary index.

## Suggested workflow

### 1. Transcribe audio/video files

```bash
python -m src.transcribe_batch courses/{slug}/input/audio --overwrite
```

### 2. Clean up transcripts

```bash
python -m src.cleanup_transcript courses/{slug}/output/transcripts \\
  --output-dir courses/{slug}/output/cleaned \\
  --markdown-output-dir courses/{slug}/output/cleaned_markdown \\
  --overwrite
```

### 3. Export ChatGPT prompts

```bash
python -m src.gpt_prompt_batch_export courses/{slug}/output/cleaned \\
  --output-dir courses/{slug}/output/gpt_prompts \\
  --overwrite
```

### 4. Import manual ChatGPT summaries

After copying a prompt into ChatGPT and saving the answer as a local `.md` file:

```bash
python -m src.import_manual_summary manual_answer.md \\
  --source-transcript courses/{slug}/output/cleaned/example.txt \\
  --output-dir courses/{slug}/output/gpt_summaries \\
  --overwrite
```

### 5. Build summary index

```bash
python -m src.build_summary_index courses/{slug}/output/gpt_summaries \\
  --output courses/{slug}/output/reports/summary_index.md \\
  --json-output courses/{slug}/output/reports/summary_index.json \\
  --overwrite
```

## Notes

- All output folders are ignored by Git except `.gitkeep` placeholders.
- You can adjust the paths in the commands to match your actual file names.
- This workflow does **not** call the OpenAI API; it is designed for manual ChatGPT interaction.

"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(commands)
    print(f"  Created course README: {readme_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a course workspace with folder structure and configuration.",
        epilog="Example: python -m src.create_course_workspace python_backend_course --title 'Python Backend Course'",
    )
    parser.add_argument(
        "course_slug",
        type=str,
        help="Course identifier (lowercase letters, numbers, hyphens, underscores)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Optional human-readable title (default: course_slug)",
    )
    parser.add_argument(
        "--overwrite-readme",
        action="store_true",
        help="Overwrite existing README.md (default: skip if exists)",
    )

    args = parser.parse_args()

    # 1. Validate slug
    if not validate_slug(args.course_slug):
        print(
            f"Error: Invalid course slug '{args.course_slug}'. "
            "Use only lowercase letters, numbers, hyphens, underscores.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Determine title
    title = args.title if args.title else args.course_slug.replace(
        "_", " ").replace("-", " ").title()

    # 3. Course root path
    course_root = Path("courses") / args.course_slug

    print(f"Creating course workspace: {args.course_slug}")
    print(f"  Title: {title}")
    print(f"  Path:  {course_root}")

    # 4. Create folder structure
    create_course_structure(course_root)

    # 5. Create config
    create_course_config(course_root, args.course_slug, title)

    # 6. Create README
    create_course_readme(course_root, args.course_slug,
                         title, args.overwrite_readme)

    print("\nCourse workspace ready.")
    print(
        f"Next steps: place audio/video files in {course_root}/input/audio/ or .../video/")
    print(f"Then run the workflow commands listed in {course_root}/README.md")


if __name__ == "__main__":
    main()
