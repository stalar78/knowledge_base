#!/usr/bin/env python3
"""
Desktop GUI prototype for GPT Course Knowledge Extractor.

Stage 6.0: First Windows‑friendly desktop GUI using Tkinter.
Wraps existing course commands without calling the OpenAI API.
"""

import subprocess
import sys
import os
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog, font


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
            self.root, text="Выбор курса", padding=10)
        ttk.Label(self.frame_course, text="Код курса:").grid(
            row=0, column=0, sticky="w")
        self.entry_slug = ttk.Entry(
            self.frame_course, textvariable=self.course_slug_var, width=30)
        self.entry_slug.grid(row=0, column=1, padx=5, pady=5)
        self.btn_create = ttk.Button(
            self.frame_course, text="Создать курс", command=self.create_course)
        self.btn_create.grid(row=0, column=2, padx=5)
        self.btn_refresh = ttk.Button(
            self.frame_course, text="Обновить статус", command=self.refresh_status)
        self.btn_refresh.grid(row=0, column=3, padx=5)
        self.btn_open_folder = ttk.Button(
            self.frame_course, text="Открыть папку курса", command=self.open_course_folder)
        self.btn_open_folder.grid(row=0, column=4, padx=5)

        # Course status area
        self.frame_status = ttk.LabelFrame(
            self.root, text="Статус курса", padding=10)
        self.status_text = scrolledtext.ScrolledText(
            self.frame_status, height=8, width=80, state="disabled")
        self.status_text.pack(fill="both", expand=True)

        # Action buttons area
        self.frame_actions = ttk.LabelFrame(
            self.root, text="Действия", padding=10)
        self.btn_transcribe = ttk.Button(
            self.frame_actions, text="Транскрибировать", command=self.transcribe)
        self.btn_transcribe.grid(row=0, column=0, padx=5, pady=5)
        self.btn_cleanup = ttk.Button(
            self.frame_actions, text="Очистить", command=self.cleanup)
        self.btn_cleanup.grid(row=0, column=1, padx=5, pady=5)
        self.btn_export_prompts = ttk.Button(
            self.frame_actions, text="Создать промпты", command=self.export_prompts)
        self.btn_export_prompts.grid(row=0, column=2, padx=5, pady=5)
        self.btn_build_index = ttk.Button(
            self.frame_actions, text="Собрать индекс", command=self.build_index)
        self.btn_build_index.grid(row=0, column=3, padx=5, pady=5)
        self.btn_import_summary = ttk.Button(
            self.frame_actions, text="Импорт summary", command=self.import_summary)
        self.btn_import_summary.grid(row=0, column=4, padx=5, pady=5)

        # Log/output area
        self.frame_log = ttk.LabelFrame(
            self.root, text="Лог / вывод", padding=10)
        self.log_text = scrolledtext.ScrolledText(
            self.frame_log, height=15, width=80)
        self.log_text.pack(fill="both", expand=True)

        # Footer link
        base_font = font.nametofont("TkDefaultFont")
        self.footer_font = base_font.copy()
        self.footer_font.configure(underline=True)
        self.footer_link = tk.Label(
            self.root,
            text="by StalarVisison",
            fg="#1a5fb4",
            cursor="hand2",
            font=self.footer_font,
            anchor="e"
        )
        self.footer_link.bind("<Button-1>", self.open_footer_link)

    def _layout_widgets(self):
        self.frame_course.pack(fill="x", padx=10, pady=10)
        self.frame_status.pack(fill="both", padx=10, pady=(0, 10), expand=True)
        self.frame_actions.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_log.pack(fill="both", padx=10, pady=(0, 6), expand=True)
        self.footer_link.pack(fill="x", padx=12, pady=(0, 8), anchor="e")

    def open_footer_link(self, _event=None):
        webbrowser.open("https://stalarvision.ru/")

    def get_slug(self):
        """Return trimmed slug, show warning if empty."""
        slug = self.course_slug_var.get().strip()
        if not slug:
            messagebox.showwarning(
                "Пустой код курса", "Введите код курса.")
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
        self.log(f"[Запуск] {cmd_str}")
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
            if result.returncode == 0:
                self.log("[Готово] Команда выполнена успешно.")
                return True
            self.log("[Ошибка] Команда завершилась с ошибкой.")
            return False
        except Exception as e:
            self.log(f"[Ошибка] Не удалось запустить команду: {e}")
            return False

    def create_course(self):
        slug = self.get_slug()
        if not slug:
            return
        title = simpledialog.askstring(
            "Название курса", "Необязательное человекочитаемое название:", initialvalue=slug)
        if title is None:  # user cancelled
            return
        args = [sys.executable, "-m", "src.create_course_workspace", slug]
        if title and title != slug:
            args.extend(["--title", title])
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Готово", f"Курс '{slug}' создан.")
        else:
            messagebox.showerror("Ошибка", "Не удалось создать курс.")

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
                "Папка не найдена", f"Папка курса не существует:\n{folder}")
            return
        try:
            os.startfile(str(folder.resolve()))
        except Exception as e:
            self.log(f"[Ошибка] Не удалось открыть папку: {e}")

    def transcribe(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Перезапись", "Перезаписать существующие транскрипты?", default=False)
        args = [sys.executable, "-m", "src.course_transcribe", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Готово", "Транскрибация завершена.")
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить транскрибацию.")

    def cleanup(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Перезапись", "Перезаписать существующие очищенные файлы?", default=False)
        args = [sys.executable, "-m", "src.course_cleanup", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Готово", "Очистка завершена.")
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить очистку.")

    def export_prompts(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Перезапись", "Перезаписать существующие файлы промптов?", default=False)
        args = [sys.executable, "-m", "src.course_export_prompts", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Готово", "Создание промптов завершено.")
        else:
            messagebox.showerror("Ошибка", "Не удалось создать промпты.")

    def build_index(self):
        slug = self.get_slug()
        if not slug:
            return
        overwrite = messagebox.askyesno(
            "Перезапись", "Перезаписать существующие файлы индекса?", default=False)
        args = [sys.executable, "-m", "src.course_build_index", slug]
        if overwrite:
            args.append("--overwrite")
        self.clear_log()
        success = self.run_command(args)
        if success:
            messagebox.showinfo("Готово", "Сборка индекса завершена.")
        else:
            messagebox.showerror("Ошибка", "Не удалось собрать индекс.")

    def import_summary(self):
        slug = self.get_slug()
        if not slug:
            return
        # Select answer file
        answer_file = filedialog.askopenfilename(
            title="Выберите файл ответа",
            filetypes=[("Markdown файлы", "*.md"),
                       ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not answer_file:
            return
        # Ask for transcript filename
        transcript = simpledialog.askstring(
            "Имя файла транскрипта",
            "Введите имя файла транскрипта (например, test.txt) или полный путь:"
        )
        if not transcript:
            return
        # Resolve path
        transcript_path = Path(transcript)
        if not transcript_path.is_absolute() and not str(transcript_path).startswith("courses/"):
            transcript_path = Path("courses") / slug / \
                "output" / "cleaned" / transcript
        overwrite = messagebox.askyesno(
            "Перезапись", "Перезаписать существующий файл summary?", default=False)
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
            messagebox.showinfo("Готово", "Импорт summary завершен.")
        else:
            messagebox.showerror("Ошибка", "Не удалось выполнить импорт summary.")


def main():
    root = tk.Tk()
    app = CourseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
