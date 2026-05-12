#!/usr/bin/env python3
"""
Console app launcher / menu for GPT Course Knowledge Extractor.

Stage 5.3: Provides an interactive menu that calls existing scripts/modules,
making the project easier to use without remembering long terminal commands.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def ask_text(prompt: str, default: Optional[str] = None) -> str:
    """
    Ask the user for text input.

    If default is provided, it will be shown in brackets.
    Returns the trimmed input, or default if input is empty and default is not None.
    """
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    try:
        answer = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInterrupted. Exiting.")
        sys.exit(0)
    if not answer and default is not None:
        return default
    return answer


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Ask a yes/no question.

    If default is True, the prompt shows "[Y/n]".
    If default is False, the prompt shows "[y/N]".
    Returns True for 'y' or 'yes', False for 'n' or 'no'.
    """
    suffix = " [Y/n]" if default else " [y/N]"
    full_prompt = prompt + suffix + ": "
    try:
        answer = input(full_prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInterrupted. Exiting.")
        sys.exit(0)
    if not answer:
        return default
    return answer in ("y", "yes")


def run_command(args: list[str]) -> bool:
    """
    Run a command using subprocess.

    Prints the command before execution.
    Waits for completion and returns True if exit code is 0, False otherwise.
    """
    cmd_str = " ".join(args)
    print(f"\n>>> {cmd_str}\n")
    try:
        result = subprocess.run(args, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print(f"Error: Command not found: {args[0]}")
        return False
    except Exception as e:
        print(f"Error executing command: {e}")
        return False


def menu_create_course() -> None:
    """Option 1: Create new course workspace."""
    print("\n--- Create new course workspace ---")
    slug = ask_text(
        "Course slug (lowercase letters, numbers, hyphens, underscores)")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    title = ask_text("Optional human-readable title",
                     default=slug.replace("_", " ").replace("-", " ").title())
    overwrite_readme = ask_yes_no(
        "Overwrite existing README.md?", default=False)

    args = [sys.executable, "-m", "src.create_course_workspace", slug]
    if title and title != slug:
        args.extend(["--title", title])
    if overwrite_readme:
        args.append("--overwrite-readme")

    success = run_command(args)
    if success:
        print("Course workspace created successfully.")
    else:
        print("Course workspace creation failed.")


def menu_workflow_status() -> None:
    """Option 2: Show course workflow status."""
    print("\n--- Show course workflow status ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    args = [sys.executable, "-m", "src.course_workflow_status", slug]
    run_command(args)


def menu_transcribe() -> None:
    """Option 4: Transcribe course."""
    print("\n--- Transcribe course ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing transcripts?", default=False)
    recursive = ask_yes_no("Scan subfolders recursively?", default=False)
    model = ask_text(
        "Model (tiny, base, small, medium, large-v2)", default="small")

    args = [sys.executable, "-m", "src.course_transcribe", slug]
    if model != "small":
        args.extend(["--model", model])
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Transcription completed successfully.")
    else:
        print("Transcription failed.")


def menu_extract_audio() -> None:
    """Option 3: Extract audio from course video files."""
    print("\n--- Extract audio from course videos ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return

    overwrite = ask_yes_no("Overwrite existing MP3 files?", default=True)
    recursive = ask_yes_no("Scan subfolders recursively?", default=False)
    bitrate = ask_text("MP3 bitrate", default="192k")

    args = [sys.executable, "-m", "src.course_extract_audio", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")
    if bitrate and bitrate != "192k":
        args.extend(["--bitrate", bitrate])

    success = run_command(args)
    if success:
        print("Audio extraction completed successfully.")
    else:
        print("Audio extraction failed.")


def menu_cleanup() -> None:
    """Option 5: Clean course transcripts."""
    print("\n--- Clean course transcripts ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing cleaned files?", default=False)
    recursive = ask_yes_no("Scan subfolders recursively?", default=False)

    args = [sys.executable, "-m", "src.course_cleanup", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Cleanup completed successfully.")
    else:
        print("Cleanup failed.")


def menu_export_prompts() -> None:
    """Option 6: Export ChatGPT prompts."""
    print("\n--- Export ChatGPT prompts ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing prompt files?", default=False)
    recursive = ask_yes_no("Scan subfolders recursively?", default=False)

    args = [sys.executable, "-m", "src.course_export_prompts", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Prompt export completed successfully.")
    else:
        print("Prompt export failed.")


def menu_import_summary() -> None:
    """Option 7: Import manual ChatGPT summary."""
    print("\n--- Import manual ChatGPT summary ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    answer_file = ask_text(
        "Path to manual answer file (e.g., manual_answer.md)")
    if not answer_file:
        print("Answer file path cannot be empty. Returning to menu.")
        return
    transcript_input = ask_text("Transcript filename or path (e.g., test.txt)")
    if not transcript_input:
        print("Transcript cannot be empty. Returning to menu.")
        return

    # Resolve transcript path
    transcript_path = Path(transcript_input)
    if not transcript_path.is_absolute() and not transcript_input.startswith("courses/"):
        # Assume it's a filename inside the course's cleaned folder
        transcript_path = Path("courses") / slug / \
            "output" / "cleaned" / transcript_input
    else:
        transcript_path = transcript_path.resolve()

    overwrite = ask_yes_no("Overwrite existing summary file?", default=False)

    output_dir = Path("courses") / slug / "output" / "gpt_summaries"
    args = [
        sys.executable,
        "-m",
        "src.import_manual_summary",
        answer_file,
        "--source-transcript",
        str(transcript_path),
        "--output-dir",
        str(output_dir),
    ]
    if overwrite:
        args.append("--overwrite")

    success = run_command(args)
    if success:
        print("Summary import completed successfully.")
    else:
        print("Summary import failed.")


def menu_build_index() -> None:
    """Option 8: Build summary index."""
    print("\n--- Build summary index ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing index files?", default=False)
    recursive = ask_yes_no("Scan subfolders recursively?", default=False)

    args = [sys.executable, "-m", "src.course_build_index", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Index build completed successfully.")
    else:
        print("Index build failed.")


def menu_export_course_analysis_prompt() -> None:
    """Option 9: Export course analysis prompt."""
    print("\n--- Export course analysis prompt ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing analysis prompt?", default=True)
    recursive = ask_yes_no("Scan summaries recursively?", default=False)

    args = [sys.executable, "-m", "src.course_export_analysis_prompt", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Course analysis prompt export completed successfully.")
    else:
        print("Course analysis prompt export failed.")


def menu_export_obsidian() -> None:
    """Option 10: Export Obsidian vault."""
    print("\n--- Export Obsidian vault ---")
    slug = ask_text("Course slug")
    if not slug:
        print("Slug cannot be empty. Returning to menu.")
        return
    overwrite = ask_yes_no("Overwrite existing export files?", default=True)
    recursive = ask_yes_no("Scan summaries recursively?", default=False)

    args = [sys.executable, "-m", "src.course_export_obsidian", slug]
    if overwrite:
        args.append("--overwrite")
    if recursive:
        args.append("--recursive")

    success = run_command(args)
    if success:
        print("Obsidian export completed successfully.")
    else:
        print("Obsidian export failed.")


def print_menu() -> None:
    """Print the main menu."""
    print("\n" + "=" * 50)
    print("GPT Course Knowledge Extractor - Console Launcher")
    print("=" * 50)
    print("1. Create new course workspace")
    print("2. Show course workflow status")
    print("3. Extract audio from video")
    print("4. Transcribe course")
    print("5. Clean course transcripts")
    print("6. Export ChatGPT prompts")
    print("7. Import manual ChatGPT summary")
    print("8. Build summary index")
    print("9. Export course analysis prompt")
    print("10. Export Obsidian vault")
    print("11. Exit")
    print("=" * 50)


def main() -> None:
    """Main loop."""
    while True:
        print_menu()
        choice = ask_text("Choose an option (1-11)", default="")
        if not choice:
            continue
        if choice == "1":
            menu_create_course()
        elif choice == "2":
            menu_workflow_status()
        elif choice == "3":
            menu_extract_audio()
        elif choice == "4":
            menu_transcribe()
        elif choice == "5":
            menu_cleanup()
        elif choice == "6":
            menu_export_prompts()
        elif choice == "7":
            menu_import_summary()
        elif choice == "8":
            menu_build_index()
        elif choice == "9":
            menu_export_course_analysis_prompt()
        elif choice == "10":
            menu_export_obsidian()
        elif choice == "11":
            print("\nExiting. Goodbye!")
            sys.exit(0)
        else:
            print(
                f"Invalid choice '{choice}'. Please enter a number between 1 and 11.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()

