#!/usr/bin/env python3
"""
Desktop GUI prototype for GPT Course Knowledge Extractor.

Stage 6.0: First Windows‑friendly desktop GUI using Tkinter.
Wraps existing course commands without calling the OpenAI API.
"""

import subprocess
import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog


class CourseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GPT Course Knowledge Extractor")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)

        # Course slug variable
        self.course_slug_var = tk.StringVar()

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):
        # Course selection area
        self.frame_course = ttk.LabelFrame(
            self.root, text="Course Selection", padding=10)
        ttk.Label(self.frame_course, text="Course slug:").grid(
            row=0, column=0, sticky="w")
        self.entry_slug = ttk.Entry(
            self.frame_course, textvariable=self.course_slug_var, width=30)
        self.entry_slug.grid(row=0, column=1, padx=5, pady=5)
        self.btn_create = ttk.Button(
            self.frame_course, text="Create course", command=self.create_course)
        self.btn_create.grid(row=0, column=2, padx=5)
        self.btn_refresh = ttk.Button(
            self.frame_course, text="Refresh status", command=self.refresh_status)
        self.btn_refresh.grid(row=0, column=3, padx=5)
        self.btn_open_folder = ttk.Button(
            self.frame_course, text="Open course folder", command=self.open_course_folder)
        self.btn_open_folder.grid(row=0, column=4, padx=5)

        # Course status area
        self.frame_status = ttk.LabelFrame(
            self.root, text="Course Status", padding=10)
        self.status_text = scrolledtext.ScrolledText(
            self.frame_status, height=8, width=80, state="disabled")
        self.status_text.pack(fill="both", expand=True)

        # Action buttons area
        self.frame_actions = ttk.LabelFrame(
            self.root, text="Actions", padding=10)
        self.btn_transcribe = ttk.Button(
            self.frame_actions, text="Transcribe", command=self.transcribe)
        self.btn_transcribe.grid(row=0, column=0, padx=5, pady=5)
        self.btn_cleanup = ttk.Button(
            self.frame_actions, text="Cleanup", command=self.cleanup)
        self.btn_cleanup.grid(row=0, column=1, padx=5, pady=5)
        self.btn_export_prompts = ttk.Button(
            self.frame_actions, text="Export prompts", command=self.export_prompts)
        self.btn_export_prompts.grid(row=0, column=2, padx=5, pady=5)
        self.btn_build_index = ttk.Button(
            self.frame_actions, text="Build index", command=self.build_index)
        self.btn_build_index.grid(row=0, column=3, padx=5, pady=5)
        self.btn_import_summary = ttk.Button(
            self.frame_actions, text="Import manual summary", command=self.import_summary)
        self.btn_import_summary.grid(row=0, column=4, padx=5, pady=5)

        # Log/output area
        self.frame_log = ttk.LabelFrame(
            self.root, text="Log / Output", padding=10)
        self.log_text = scrolledtext.ScrolledText(
            self.frame_log, height=15, width=80)
        self.log_text.pack(fill="both", expand=True)

    def _layout_widgets(self):
        self.frame_course.pack(fill="x", padx=10, pady=10)
        self.frame_status.pack(fill="both", padx=10, pady=(0, 10), expand=True)
        self.frame_actions.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_log.pack(fill="both", padx=10, pady=(0, 10), expand=True)

    def get_slug(self):
        """Return trimmed slug, show warning if empty."""
        slug = self.course_slug_var.get().strip()
        if not slug:
            messagebox.showwarning(
                "Missing slug", "Please enter a course slug.")
            return None
        return slug

    def log(self, message):
        """Append message to log area."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear log area."""
        self.log_text.delete(1.0, tk.END)

    def run_command(self, args):
        """
        Run a command via subprocess, log output, return success.
        """
        cmd_str = " ".join(args)
        self.log(f">>> {cmd_str}")
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")
            self.log(f"Return code: {result.returncode}")
            return result.returncode == 0
        except Exception as e:
            self.log(f"Error executing command: {e}")
            return False

    def create_course(self):
        slug = self.get_slug()
        if not slug:
            return
        title = simpledialog.askstring(
            "Course title", "Optional human-readable title:", initialvalue=slug)
        if title is None:  # user cancelled
            return
        args = [sys.executable, "-m", "src.create_course_workspace", slug]
        if title and title != slug:
            args.extend(["--title", title])
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", f"Course '{slug}' created.")
        else:
            messagebox.showerror("Error", "Course creation failed.")

    def refresh_status(self):
        slug = self.get_slug()
        if not slug:
            return
        self.clear_log()
        args = [sys.executable, "-m", "src.course_workflow_status", slug]
        self.run_command(args)

    def open_course_folder(self):
        slug = self.get_slug()
        if not slug:
            return
        folder = Path("courses") / slug
        if not folder.exists():
            messagebox.showwarning(
                "Folder not found", f"Course folder does not exist:\n{folder}")
            return
        try:
            os.startfile(str(folder.resolve()))
        except Exception as e:
            self.log(f"Failed to open folder: {e}")

    def transcribe(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Overwrite?", "Overwrite existing transcripts?", default=False)
        args = [sys.executable, "-m", "src.course_transcribe", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", "Transcription completed.")
        else:
            messagebox.showerror("Error", "Transcription failed.")

    def cleanup(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Overwrite?", "Overwrite existing cleaned files?", default=False)
        args = [sys.executable, "-m", "src.course_cleanup", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", "Cleanup completed.")
        else:
            messagebox.showerror("Error", "Cleanup failed.")

    def export_prompts(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Overwrite?", "Overwrite existing prompt files?", default=False)
        args = [sys.executable, "-m", "src.course_export_prompts", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", "Prompt export completed.")
        else:
            messagebox.showerror("Error", "Prompt export failed.")

    def build_index(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Overwrite?", "Overwrite existing index files?", default=False)
        args = [sys.executable, "-m", "src.course_build_index", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", "Index build completed.")
        else:
            messagebox.showerror("Error", "Index build failed.")

    def import_summary(self):
        slug = self.get_slug()
        if not slug:
            return
        # Select answer file
        answer_file = filedialog.askopenfilename(
            title="Select manual answer file",
            filetypes=[("Markdown files", "*.md"),
                       ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not answer_file:
            return
        # Ask for transcript filename
        transcript = simpledialog.askstring(
            "Transcript filename",
            "Enter transcript filename (e.g., test.txt) or full path:"
        )
        if not transcript:
            return
        # Resolve path
        transcript_path = Path(transcript)
        if not transcript_path.is_absolute() and not str(transcript_path).startswith("courses/"):
            transcript_path = Path("courses") / slug / \
                "output" / "cleaned" / transcript
        overwrite = messagebox.askyesno(
            "Overwrite?", "Overwrite existing summary file?", default=False)
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
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Success", "Summary import completed.")
        else:
            messagebox.showerror("Error", "Summary import failed.")


def main():
    root = tk.Tk()
    app = CourseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
