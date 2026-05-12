#!/usr/bin/env python3
"""
Reusable Obsidian export helpers for course workspaces.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def safe_note_name(name: str) -> str:
    """Convert arbitrary text into a filesystem-safe note name."""
    cleaned = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", name.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")
    return cleaned or "untitled"


def read_text(path: Path) -> str:
    """Read UTF-8 text from file."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str, overwrite: bool = False) -> str:
    """Write UTF-8 text and return 'written' or 'skipped'."""
    if path.exists() and not overwrite:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return "written"


def discover_markdown_files(folder: Path, recursive: bool = False) -> list[Path]:
    """Discover markdown files in folder."""
    if not folder.is_dir():
        return []
    pattern = "**/*.md" if recursive else "*.md"
    files = [p for p in folder.glob(pattern) if p.is_file()]
    files.sort(key=lambda p: str(p).lower())
    return files


def build_course_home_note(course_slug: str, course_title: str, exported_files: dict[str, list[Path]]) -> str:
    """Build Obsidian home note for the course export."""
    now_iso = datetime.now(timezone.utc).isoformat()
    lesson_links = exported_files.get("lesson_notes", [])

    lines = [
        "# Course Home",
        "",
        f"- Course title: `{course_title}`",
        f"- Course slug: `{course_slug}`",
        f"- Export timestamp (UTC): `{now_iso}`",
        "",
        "## Core Notes",
        "- [[01_Summary_Index]]",
        "- [[02_Course_Analysis_Prompt]]",
        "",
        "## Lesson Notes",
    ]
    if lesson_links:
        lines.extend([f"- [[Lessons/{path.stem}]]" for path in lesson_links])
    else:
        lines.append("- No lesson notes were exported.")

    lines.extend(
        [
            "",
            "## Structure",
            "- `Lessons/` contains transformed lesson summary notes with backlinks.",
            "- `Source/` contains exact source markdown copies used for export.",
            "- `_meta/export_manifest.json` contains export metadata and file lists.",
            "",
            "## Next steps",
            "1. Copy the `[[02_Course_Analysis_Prompt]]` content into ChatGPT.",
            "2. Save the course-level answer manually into your knowledge workflow.",
            "3. Future: enrich the Obsidian vault with course map and term notes.",
            "",
        ]
    )
    return "\n".join(lines)


def build_lesson_note(source_path: Path, source_text: str, course_slug: str) -> str:
    """Build transformed lesson note."""
    title = source_path.stem
    lines = [
        f"# Lesson Summary: {title}",
        "",
        f"- Course: `{course_slug}`",
        f"- Source file: `{source_path.name}`",
        "- Backlink: [[00_Course_Home]]",
        "",
        "## Original Summary",
        "",
        source_text.strip(),
        "",
        "## Links / Concepts",
        "Add backlinks to related concepts after course-level analysis.",
        "",
    ]
    return "\n".join(lines)


def build_index_note(summary_index_text: str, course_slug: str) -> str:
    """Build summary index note for Obsidian."""
    lines = [
        "# Summary Index",
        "",
        f"- Course: `{course_slug}`",
        "- Backlink: [[00_Course_Home]]",
        "",
        "## Original summary_index.md",
        "",
        summary_index_text.strip(),
        "",
    ]
    return "\n".join(lines)


def build_prompt_note(prompt_text: str, course_slug: str) -> str:
    """Build course analysis prompt note for Obsidian."""
    lines = [
        "# Course Analysis Prompt",
        "",
        f"- Course: `{course_slug}`",
        "- Backlink: [[00_Course_Home]]",
        "",
        "Copy this prompt into ChatGPT to generate course-level analysis.",
        "",
        "## Prompt Content",
        "",
        prompt_text.strip(),
        "",
    ]
    return "\n".join(lines)


def export_course_to_obsidian(
    *,
    course_slug: str,
    course_title: str,
    summary_index_path: Path,
    summary_files: list[Path],
    analysis_prompt_path: Path | None,
    output_dir: Path,
    overwrite: bool = False,
    recursive: bool = False,
) -> dict[str, Any]:
    """Export a course workspace into an Obsidian-ready structure."""
    exported_at = datetime.now(timezone.utc).isoformat()

    lessons_dir = output_dir / "Lessons"
    source_dir = output_dir / "Source"
    source_summaries_dir = source_dir / "summaries"
    meta_dir = output_dir / "_meta"

    written = 0
    skipped = 0
    exported_files: dict[str, list[Path]] = {
        "lesson_notes": [],
        "source_summaries": [],
        "core_notes": [],
        "source_core": [],
        "meta": [],
    }

    summary_index_text = read_text(summary_index_path)
    analysis_prompt_missing = analysis_prompt_path is None or not analysis_prompt_path.is_file()
    if analysis_prompt_missing:
        analysis_prompt_text = (
            "Промпт анализа курса пока не создан.\n\n"
            "Сначала выполните команду:\n"
            f"`python -m src.course_export_analysis_prompt {course_slug} --overwrite`"
        )
    else:
        analysis_prompt_text = read_text(analysis_prompt_path)

    index_note = build_index_note(summary_index_text, course_slug)
    prompt_note = build_prompt_note(analysis_prompt_text, course_slug)

    status = write_text(output_dir / "01_Summary_Index.md", index_note, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["core_notes"].append(Path("01_Summary_Index.md"))

    status = write_text(output_dir / "02_Course_Analysis_Prompt.md", prompt_note, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["core_notes"].append(Path("02_Course_Analysis_Prompt.md"))

    # Source files: core
    status = write_text(source_dir / "summary_index.md", summary_index_text, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["source_core"].append(Path("Source/summary_index.md"))

    status = write_text(source_dir / "course_analysis_prompt.md", analysis_prompt_text, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["source_core"].append(Path("Source/course_analysis_prompt.md"))

    # Lesson/source summary files
    source_files_list: list[str] = [str(summary_index_path)]
    if analysis_prompt_path is not None:
        source_files_list.append(str(analysis_prompt_path))

    for summary_path in summary_files:
        source_text = read_text(summary_path)
        source_files_list.append(str(summary_path))

        lesson_file = lessons_dir / f"{safe_note_name(summary_path.stem)}.md"
        lesson_text = build_lesson_note(summary_path, source_text, course_slug)
        status = write_text(lesson_file, lesson_text, overwrite=overwrite)
        written += 1 if status == "written" else 0
        skipped += 1 if status == "skipped" else 0
        exported_files["lesson_notes"].append(Path("Lessons") / lesson_file.name)

        source_summary_file = source_summaries_dir / summary_path.name
        status = write_text(source_summary_file, source_text, overwrite=overwrite)
        written += 1 if status == "written" else 0
        skipped += 1 if status == "skipped" else 0
        exported_files["source_summaries"].append(Path("Source/summaries") / summary_path.name)

    home_note = build_course_home_note(course_slug, course_title, exported_files)
    status = write_text(output_dir / "00_Course_Home.md", home_note, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["core_notes"].append(Path("00_Course_Home.md"))

    manifest = {
        "course_slug": course_slug,
        "course_title": course_title,
        "exported_at": exported_at,
        "source_files": source_files_list,
        "exported_files": {k: [str(p) for p in v] for k, v in exported_files.items()},
        "counts": {
            "summaries": len(summary_files),
            "lesson_notes": len(exported_files["lesson_notes"]),
            "source_files": len(source_files_list),
        },
        "overwrite": overwrite,
        "recursive": recursive,
        "analysis_prompt_missing": analysis_prompt_missing,
    }
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False)
    status = write_text(meta_dir / "export_manifest.json", manifest_text, overwrite=overwrite)
    written += 1 if status == "written" else 0
    skipped += 1 if status == "skipped" else 0
    exported_files["meta"].append(Path("_meta/export_manifest.json"))

    return {
        "written": written,
        "skipped": skipped,
        "summaries": len(summary_files),
        "output_dir": output_dir,
        "analysis_prompt_missing": analysis_prompt_missing,
    }
