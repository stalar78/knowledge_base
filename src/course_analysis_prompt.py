#!/usr/bin/env python3
"""
Helpers for building a manual course-level analysis prompt.
"""

from pathlib import Path


def discover_summary_files(summary_dir: Path, recursive: bool = False) -> list[Path]:
    """Discover summary markdown files in a directory."""
    if not summary_dir.is_dir():
        return []

    pattern = "**/*.md" if recursive else "*.md"
    files = [p for p in summary_dir.glob(pattern) if p.is_file()]
    files.sort(key=lambda p: str(p).lower())
    return files


def read_text(path: Path) -> str:
    """Read UTF-8 text from a file."""
    return path.read_text(encoding="utf-8")


def build_course_analysis_prompt(
    course_slug: str,
    course_title: str,
    summary_index_text: str,
    summaries: list[tuple[Path, str]],
) -> str:
    """Build the full markdown prompt for manual ChatGPT course analysis."""
    sections = []
    sections.append("# Course-Level Analysis Prompt")
    sections.append("")
    sections.append("## Context")
    sections.append(f"- Course slug: `{course_slug}`")
    sections.append(f"- Course title: `{course_title}`")
    sections.append(f"- Number of lesson summaries: `{len(summaries)}`")
    sections.append("")
    sections.append("## Critical Rules")
    sections.append("- Use only the materials provided below.")
    sections.append("- Do not invent facts beyond the provided summaries and summary index.")
    sections.append("- If something is uncertain or missing, explicitly mark it as `needs verification`.")
    sections.append("- Keep analysis faithful to source wording and meaning.")
    sections.append("")
    sections.append("## Required Output Structure")
    sections.append("Please produce your response in Markdown with these sections:")
    sections.append("1. Course overview")
    sections.append("2. Main knowledge map")
    sections.append("3. Key themes and concepts")
    sections.append("4. Lesson-by-lesson synthesis")
    sections.append("5. Cross-lesson connections")
    sections.append("6. Repeated ideas and patterns")
    sections.append("7. Practical actions / exercises")
    sections.append("8. Important terms and definitions")
    sections.append("9. Gaps, unclear points, and questions for further study")
    sections.append("10. Suggested learning path / review plan")
    sections.append("11. Obsidian-ready structure")
    sections.append("   - suggested folders")
    sections.append("   - suggested notes")
    sections.append("   - backlinks / relations between notes")
    sections.append("")
    sections.append("## Source: summary_index.md")
    sections.append("```markdown")
    sections.append(summary_index_text.strip())
    sections.append("```")
    sections.append("")
    sections.append("## Source: Lesson Summaries")

    for summary_path, summary_text in summaries:
        sections.append("")
        sections.append(f"### File: `{summary_path.name}`")
        sections.append("```markdown")
        sections.append(summary_text.strip())
        sections.append("```")

    sections.append("")
    sections.append("## Final Reminder")
    sections.append("If any claim cannot be grounded in the source materials above, mark it as `needs verification`.")
    sections.append("")
    return "\n".join(sections)
