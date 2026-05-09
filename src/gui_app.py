#!/usr/bin/env python3
"""
Desktop GUI prototype for GPT Course Knowledge Extractor.

Stage 6.0: First Windows-friendly desktop GUI using Tkinter.
Wraps existing course commands without calling the OpenAI API.
"""

import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk


class CourseGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GPT Course Knowledge Extractor")
        self.root.geometry("900x700")
        self.root.minsize(800, 550)

        self.course_slug_var = tk.StringVar()
        self.progress_var = tk.IntVar(value=0)
        self.command_running = False
        self.action_buttons: list[ttk.Button] = []

        self.main_frame = ttk.Frame(self.root)
        self.footer_frame = ttk.Frame(self.root)

        self._create_widgets()
        self._layout_widgets()
        self.set_progress_idle()

    def _create_widgets(self) -> None:
        self.frame_course = ttk.LabelFrame(self.main_frame, text="Выбор курса", padding=10)
        ttk.Label(self.frame_course, text="Код курса:").grid(row=0, column=0, sticky="w")

        self.entry_slug = ttk.Entry(self.frame_course, textvariable=self.course_slug_var, width=30)
        self.entry_slug.grid(row=0, column=1, padx=5, pady=5)

        self.btn_create = ttk.Button(self.frame_course, text="Создать курс", command=self.create_course)
        self.btn_create.grid(row=0, column=2, padx=5)

        self.btn_refresh = ttk.Button(self.frame_course, text="Обновить статус", command=self.refresh_status)
        self.btn_refresh.grid(row=0, column=3, padx=5)

        self.btn_open_folder = ttk.Button(
            self.frame_course,
            text="Открыть папку курса",
            command=self.open_course_folder,
        )
        self.btn_open_folder.grid(row=0, column=4, padx=5)

        self.btn_help = ttk.Button(self.frame_course, text="Инструкция", command=self.show_instructions)
        self.btn_help.grid(row=0, column=5, padx=5)

        self.frame_status = ttk.LabelFrame(self.main_frame, text="Статус курса", padding=10)
        self.status_text = scrolledtext.ScrolledText(self.frame_status, height=8, width=80, state="disabled")
        self.status_text.pack(fill="both", expand=True)

        self.frame_actions = ttk.LabelFrame(self.main_frame, text="Действия", padding=10)
        self.btn_transcribe = ttk.Button(self.frame_actions, text="Транскрибировать", command=self.transcribe)
        self.btn_transcribe.grid(row=0, column=0, padx=5, pady=5)

        self.btn_cleanup = ttk.Button(self.frame_actions, text="Очистить", command=self.cleanup)
        self.btn_cleanup.grid(row=0, column=1, padx=5, pady=5)

        self.btn_export_prompts = ttk.Button(self.frame_actions, text="Создать промпты", command=self.export_prompts)
        self.btn_export_prompts.grid(row=0, column=2, padx=5, pady=5)

        self.btn_build_index = ttk.Button(self.frame_actions, text="Собрать индекс", command=self.build_index)
        self.btn_build_index.grid(row=0, column=3, padx=5, pady=5)

        self.btn_import_summary = ttk.Button(self.frame_actions, text="Импорт summary", command=self.import_summary)
        self.btn_import_summary.grid(row=0, column=4, padx=5, pady=5)

        self.frame_progress = ttk.LabelFrame(self.main_frame, text="Прогресс", padding=10)
        self.progress_label = ttk.Label(self.frame_progress, text="Прогресс: 0%")
        self.progress_label.pack(anchor="w", pady=(0, 4))
        self.progress_bar = ttk.Progressbar(
            self.frame_progress,
            mode="determinate",
            maximum=100,
            variable=self.progress_var,
        )
        self.progress_bar.pack(fill="x")

        self.frame_log = ttk.LabelFrame(self.main_frame, text="Лог / вывод", padding=10)
        self.log_text = scrolledtext.ScrolledText(self.frame_log, height=14, width=80)
        self.log_text.pack(fill="both", expand=True)

        self.footer_label = tk.Label(
            self.footer_frame,
            text="by StalarVision",
            fg="#1a0dab",
            cursor="hand2",
            font=("TkDefaultFont", 9, "underline"),
        )
        self.footer_label.pack(side="right")
        self.footer_label.bind("<Button-1>", lambda event: webbrowser.open("https://stalarvision.ru/"))

        self.action_buttons = [
            self.btn_create,
            self.btn_refresh,
            self.btn_open_folder,
            self.btn_help,
            self.btn_transcribe,
            self.btn_cleanup,
            self.btn_export_prompts,
            self.btn_build_index,
            self.btn_import_summary,
        ]

    def _layout_widgets(self) -> None:
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 6))
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.frame_course.pack(fill="x", padx=10, pady=10)
        self.frame_status.pack(fill="both", padx=10, pady=(0, 10), expand=True)
        self.frame_actions.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_progress.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_log.pack(fill="both", padx=10, pady=(0, 8), expand=True)

    def show_instructions(self) -> None:
        instructions = (
            "1. Создайте курс.\n"
            "2. Откройте папку курса.\n"
            "3. Положите MP3 в input/audio или видео в input/video.\n"
            "4. Нажмите \"Транскрибировать\".\n"
            "5. Нажмите \"Очистить\".\n"
            "6. Нажмите \"Создать промпты\".\n"
            "7. Откройте prompt-файл и вставьте его в ChatGPT.\n"
            "8. Сохраните ответ ChatGPT в .md или .txt.\n"
            "9. Нажмите \"Импорт summary\".\n"
            "10. Нажмите \"Собрать индекс\"."
        )
        messagebox.showinfo("Инструкция", instructions)

    def set_actions_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for button in self.action_buttons:
            button.configure(state=state)

    def set_progress_idle(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_var.set(0)
        self.progress_label.configure(text="Прогресс: 0%")

    def set_progress_running(self) -> None:
        self.progress_var.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)
        self.progress_label.configure(text="Прогресс: выполняется...")

    def set_progress_success(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_var.set(100)
        self.progress_label.configure(text="Прогресс: 100%")

    def set_progress_error(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_var.set(0)
        self.progress_label.configure(text="Прогресс: ошибка")

    def log(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self) -> None:
        self.log_text.delete(1.0, tk.END)

    def _set_status_text(self, text: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, text)
        self.status_text.see(tk.END)
        self.status_text.configure(state="disabled")

    def get_slug(self) -> str | None:
        slug = self.course_slug_var.get().strip()
        if not slug:
            messagebox.showwarning("Не указан код курса", "Введите код курса.")
            return None
        return slug

    def prepare_action(self, start_message: str, is_transcribe: bool = False) -> bool:
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return False

        self.clear_log()
        self.set_progress_idle()
        self.log(start_message)
        self.log("[Запуск] Команда выполняется. Для длинных аудио это может занять много времени.")
        if is_transcribe:
            self.log("[Важно] Транскрибация длинного файла на CPU может занять 20-60 минут.")
        return True

    def run_command_async(
        self,
        args: list[str],
        on_success_message: str,
        on_fail_message: str,
        update_status: bool = False,
    ) -> None:
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.command_running = True
        self.set_actions_enabled(False)
        self.log(f"[Команда] {' '.join(args)}")
        self.set_progress_running()

        def worker() -> None:
            try:
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"
                result = subprocess.run(
                    args,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                stdout = result.stdout or ""
                stderr = result.stderr or ""
                return_code = result.returncode
                error = None
            except Exception as exc:
                stdout = ""
                stderr = ""
                return_code = None
                error = str(exc)

            self.root.after(
                0,
                lambda: self._finish_command(
                    stdout,
                    stderr,
                    return_code,
                    error,
                    on_success_message,
                    on_fail_message,
                    update_status,
                ),
            )

        threading.Thread(target=worker, daemon=True).start()

    def _finish_command(
        self,
        stdout: str,
        stderr: str,
        return_code: int | None,
        error: str | None,
        on_success_message: str,
        on_fail_message: str,
        update_status: bool,
    ) -> None:
        if stdout.strip():
            self.log(stdout.rstrip())
        if stderr.strip():
            self.log(f"STDERR:\n{stderr.rstrip()}")
        if return_code is not None:
            self.log(f"Return code: {return_code}")
        if error:
            self.log(f"[Ошибка] Не удалось запустить команду: {error}")

        success = (return_code == 0) and (error is None)
        if success:
            self.set_progress_success()
            self.log("[Готово] Команда выполнена успешно.")
            if update_status:
                self._set_status_text(stdout or "Статус курса обновлен.")
            messagebox.showinfo("Готово", on_success_message)
        else:
            self.set_progress_error()
            self.log("[Ошибка] Команда завершилась с ошибкой.")
            messagebox.showerror("Ошибка", on_fail_message)

        self.command_running = False
        self.set_actions_enabled(True)

    def create_course(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        title = simpledialog.askstring("Создать курс", "Введите название курса (необязательно):", initialvalue=slug)
        if title is None:
            return

        if not self.prepare_action("Запуск создания курса..."):
            return

        args = [sys.executable, "-m", "src.create_course_workspace", slug]
        if title and title != slug:
            args.extend(["--title", title])
        self.run_command_async(args, f"Курс '{slug}' создан.", "Не удалось создать курс.")

    def refresh_status(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск обновления статуса курса..."):
            return

        args = [sys.executable, "-m", "src.course_workflow_status", slug]
        self.run_command_async(
            args,
            "Статус курса обновлен.",
            "Не удалось обновить статус курса.",
            update_status=True,
        )

    def open_course_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.clear_log()
        self.set_progress_idle()
        self.log("Открытие папки курса...")

        folder = Path("courses") / slug
        if not folder.exists():
            self.log("[Ошибка] Папка курса не существует.")
            messagebox.showwarning("Папка не найдена", f"Папка курса не существует:\n{folder}")
            return

        try:
            os.startfile(str(folder.resolve()))
            self.set_progress_success()
            self.log(f"[Готово] Папка открыта: {folder}")
        except Exception as exc:
            self.set_progress_error()
            self.log(f"[Ошибка] Не удалось открыть папку: {exc}")
            messagebox.showerror("Ошибка", "Не удалось открыть папку курса.")

    def transcribe(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск транскрибации курса...", is_transcribe=True):
            return

        args = [sys.executable, "-m", "src.course_transcribe", slug, "--overwrite"]
        self.run_command_async(args, "Транскрибация завершена.", "Не удалось выполнить транскрибацию.")

    def cleanup(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск очистки курса..."):
            return

        args = [sys.executable, "-m", "src.course_cleanup", slug, "--overwrite"]
        self.run_command_async(args, "Очистка завершена.", "Не удалось выполнить очистку.")

    def export_prompts(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск создания промптов..."):
            return

        args = [sys.executable, "-m", "src.course_export_prompts", slug, "--overwrite"]
        self.run_command_async(args, "Создание промптов завершено.", "Не удалось создать промпты.")

    def build_index(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск сборки индекса..."):
            return

        args = [sys.executable, "-m", "src.course_build_index", slug, "--overwrite"]
        self.run_command_async(args, "Сборка индекса завершена.", "Не удалось собрать индекс.")

    def import_summary(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        answer_file = filedialog.askopenfilename(
            title="Выберите файл с ответом ChatGPT",
            filetypes=[
                ("Markdown файлы", "*.md"),
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*"),
            ],
        )
        if not answer_file:
            return

        transcript = simpledialog.askstring(
            "Имя транскрипта",
            "Введите имя очищенного транскрипта, например: lesson_01.txt",
        )
        if not transcript:
            return

        transcript_path = Path(transcript)
        transcript_parts = transcript_path.parts
        transcript_in_courses = len(transcript_parts) > 0 and transcript_parts[0] == "courses"
        if not transcript_path.is_absolute() and not transcript_in_courses:
            transcript_path = Path("courses") / slug / "output" / "cleaned" / transcript

        if not self.prepare_action("Запуск импорта summary..."):
            return

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
            "--overwrite",
        ]
        self.run_command_async(args, "Импорт summary завершен.", "Не удалось выполнить импорт summary.")


def main() -> None:
    root = tk.Tk()
    CourseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
