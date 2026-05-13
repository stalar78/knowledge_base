#!/usr/bin/env python3
"""
Desktop GUI prototype for GPT Course Knowledge Extractor.

Stage 6.0: First Windows-friendly desktop GUI using Tkinter.
Wraps existing course commands without calling the OpenAI API.
"""

import os
import subprocess
import threading
import webbrowser
from pathlib import Path
from typing import Literal
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk

try:
    from src.runtime_environment import build_module_command, ensure_app_cwd
    from src.extract_audio import discover_video_files as discover_video_files_impl
    from src.utils.supported_formats import is_supported_audio_file
except ModuleNotFoundError:
    from runtime_environment import build_module_command, ensure_app_cwd
    from extract_audio import discover_video_files as discover_video_files_impl
    from utils.supported_formats import is_supported_audio_file


def get_subprocess_startup_kwargs() -> dict:
    if os.name != "nt":
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


class CourseGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GPT Course Knowledge Extractor")
        self.root.geometry("1200x820")
        self.root.minsize(1050, 720)

        self.course_slug_var = tk.StringVar()
        self.progress_var = tk.IntVar(value=0)
        self.command_running = False
        self.action_buttons: list[ttk.Button] = []

        self.main_frame = ttk.Frame(self.root)
        self.footer_frame = ttk.Frame(self.root)

        self._create_widgets()
        self._layout_widgets()
        self.set_progress_idle()

    def create_group(self, parent: ttk.Widget, title: str, row: int, column: int, weight: int = 1) -> ttk.LabelFrame:
        group = ttk.LabelFrame(parent, text=title, padding=8)
        group.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")
        parent.grid_columnconfigure(column, weight=weight)
        return group

    def _create_widgets(self) -> None:
        self.frame_course = ttk.LabelFrame(self.main_frame, text="Выбор курса", padding=10)
        ttk.Label(self.frame_course, text="Код курса:").grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.entry_slug = ttk.Entry(self.frame_course, textvariable=self.course_slug_var, width=30)
        self.entry_slug.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_create = ttk.Button(self.frame_course, text="Создать курс", command=self.create_course)
        self.btn_create.grid(row=0, column=2, padx=5, pady=5)

        self.btn_refresh = ttk.Button(self.frame_course, text="Обновить статус", command=self.refresh_status)
        self.btn_refresh.grid(row=0, column=3, padx=5, pady=5)

        self.btn_open_folder = ttk.Button(
            self.frame_course,
            text="Открыть папку",
            command=self.open_course_folder,
        )
        self.btn_open_folder.grid(row=0, column=4, padx=5, pady=5)

        self.btn_help = ttk.Button(self.frame_course, text="Инструкция", command=self.show_instructions)
        self.btn_help.grid(row=0, column=5, padx=5, pady=5)
        self.frame_course.grid_columnconfigure(1, weight=1)

        self.frame_actions = ttk.LabelFrame(self.main_frame, text="Процесс обработки", padding=10)
        self.frame_actions.grid_columnconfigure(0, weight=1)
        self.frame_actions.grid_columnconfigure(1, weight=1)
        self.frame_actions.grid_columnconfigure(2, weight=1)
        self.frame_actions.grid_columnconfigure(3, weight=1)

        group_prepare = self.create_group(self.frame_actions, "1. Подготовка", row=0, column=0)
        group_process = self.create_group(self.frame_actions, "2. Обработка", row=0, column=1)
        group_gpt = self.create_group(self.frame_actions, "3. GPT вручную", row=0, column=2)
        group_analysis = self.create_group(self.frame_actions, "4. Анализ и экспорт", row=0, column=3)

        self.btn_extract_audio = ttk.Button(group_prepare, text="Извлечь аудио", command=self.extract_audio)
        self.btn_extract_audio.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        group_prepare.grid_columnconfigure(0, weight=1)

        self.btn_transcribe = ttk.Button(group_process, text="Транскрибировать", command=self.transcribe)
        self.btn_transcribe.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_cleanup = ttk.Button(group_process, text="Очистить", command=self.cleanup)
        self.btn_cleanup.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        group_process.grid_columnconfigure(0, weight=1)

        self.btn_export_prompts = ttk.Button(group_gpt, text="Создать промпты", command=self.export_prompts)
        self.btn_export_prompts.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_import_summary = ttk.Button(group_gpt, text="Импорт summary", command=self.import_summary)
        self.btn_import_summary.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        group_gpt.grid_columnconfigure(0, weight=1)

        self.btn_build_index = ttk.Button(group_analysis, text="Собрать индекс", command=self.build_index)
        self.btn_build_index.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_course_analysis_prompt = ttk.Button(
            group_analysis,
            text="Промпт анализа курса",
            command=self.export_course_analysis_prompt,
        )
        self.btn_course_analysis_prompt.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self.btn_export_obsidian = ttk.Button(
            group_analysis,
            text="Экспорт Obsidian",
            command=self.export_obsidian,
        )
        self.btn_export_obsidian.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        group_analysis.grid_columnconfigure(0, weight=1)

        self.frame_results = ttk.LabelFrame(self.main_frame, text="Результаты", padding=10)
        self.frame_results.grid_columnconfigure(0, weight=1)
        self.frame_results.grid_columnconfigure(1, weight=1)
        self.frame_results.grid_columnconfigure(2, weight=1)

        group_sources = self.create_group(self.frame_results, "Исходники", row=0, column=0)
        group_gpt_materials = self.create_group(self.frame_results, "GPT материалы", row=0, column=1)
        group_reports_export = self.create_group(self.frame_results, "Отчёты и экспорт", row=0, column=2)

        self.btn_open_video = ttk.Button(group_sources, text="Открыть video", command=self.open_video_folder)
        self.btn_open_video.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_open_audio = ttk.Button(group_sources, text="Открыть audio", command=self.open_audio_folder)
        self.btn_open_audio.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        group_sources.grid_columnconfigure(0, weight=1)

        self.btn_open_prompts = ttk.Button(group_gpt_materials, text="Открыть prompts", command=self.open_prompts_folder)
        self.btn_open_prompts.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_open_summaries = ttk.Button(group_gpt_materials, text="Открыть summaries", command=self.open_summaries_folder)
        self.btn_open_summaries.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        group_gpt_materials.grid_columnconfigure(0, weight=1)

        self.btn_open_reports = ttk.Button(group_reports_export, text="Открыть reports", command=self.open_reports_folder)
        self.btn_open_reports.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.btn_open_summary_index = ttk.Button(
            group_reports_export,
            text="Открыть summary_index.md",
            command=self.open_summary_index,
        )
        self.btn_open_summary_index.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        self.btn_open_analysis_prompt = ttk.Button(
            group_reports_export,
            text="Открыть analysis prompt",
            command=self.open_analysis_prompt,
        )
        self.btn_open_analysis_prompt.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        self.btn_open_obsidian_export = ttk.Button(
            group_reports_export,
            text="Открыть Obsidian export",
            command=self.open_obsidian_export,
        )
        self.btn_open_obsidian_export.grid(row=3, column=0, padx=4, pady=4, sticky="ew")
        group_reports_export.grid_columnconfigure(0, weight=1)

        self.frame_status_progress = ttk.Frame(self.main_frame)
        self.frame_status_progress.grid_columnconfigure(0, weight=2)
        self.frame_status_progress.grid_columnconfigure(1, weight=1)

        self.frame_status = ttk.LabelFrame(self.frame_status_progress, text="Статус курса", padding=10)
        self.status_text = scrolledtext.ScrolledText(self.frame_status, height=8, width=80, state="disabled")
        self.status_text.pack(fill="both", expand=True)

        self.frame_progress = ttk.LabelFrame(self.frame_status_progress, text="Прогресс", padding=10)
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
        self.log_text = scrolledtext.ScrolledText(self.frame_log, height=10, width=80)
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
            self.btn_extract_audio,
            self.btn_transcribe,
            self.btn_cleanup,
            self.btn_export_prompts,
            self.btn_import_summary,
            self.btn_build_index,
            self.btn_course_analysis_prompt,
            self.btn_export_obsidian,
            self.btn_open_video,
            self.btn_open_audio,
            self.btn_open_prompts,
            self.btn_open_summaries,
            self.btn_open_reports,
            self.btn_open_summary_index,
            self.btn_open_analysis_prompt,
            self.btn_open_obsidian_export,
        ]

    def _layout_widgets(self) -> None:
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 6))
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.frame_course.pack(fill="x", padx=10, pady=10)
        self.frame_actions.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_results.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_status_progress.pack(fill="x", padx=10, pady=(0, 10))
        self.frame_status.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.frame_progress.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.frame_log.pack(fill="both", padx=10, pady=(0, 8), expand=True)

    def show_instructions(self) -> None:
        instructions = (
            "1. Создайте курс.\n"
            "2. Откройте папку курса.\n"
            "3. Положите видео в input/video или MP3 в input/audio.\n"
            "4. Если добавлены видео, нажмите \"Извлечь аудио\".\n"
            "5. Нажмите \"Транскрибировать\".\n"
            "6. Нажмите \"Очистить\".\n"
            "7. Нажмите \"Создать промпты\".\n"
            "8. Скопируйте prompt в ChatGPT и сохраните ответ.\n"
            "9. Нажмите \"Импорт summary\".\n"
            "10. Нажмите \"Собрать индекс\".\n"
            "11. Нажмите \"Промпт анализа курса\".\n"
            "12. При необходимости вставьте course-level prompt в ChatGPT.\n"
            "13. Нажмите \"Экспорт Obsidian\".\n"
            "14. Откройте Obsidian export."
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
                startup_kwargs = get_subprocess_startup_kwargs()
                result = subprocess.run(
                    args,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    **startup_kwargs,
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

        args = build_module_command("src.create_course_workspace", slug)
        if title and title != slug:
            args.extend(["--title", title])
        self.run_command_async(args, f"Курс '{slug}' создан.", "Не удалось создать курс.")

    def refresh_status(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск обновления статуса курса..."):
            return

        args = build_module_command("src.course_workflow_status", slug)
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

    def open_path(self, path: Path, missing_title: str, missing_message: str, success_message: str) -> None:
        slug = self.get_slug()
        if not slug:
            return
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.clear_log()
        self.set_progress_idle()

        if not path.exists():
            self.log(f"[Предупреждение] {missing_message}")
            messagebox.showwarning(missing_title, missing_message)
            return

        try:
            os.startfile(str(path.resolve()))
            self.set_progress_success()
            self.log(f"[Готово] {success_message}")
        except Exception as exc:
            self.set_progress_error()
            self.log(f"[Ошибка] Не удалось открыть путь: {exc}")
            messagebox.showerror("Ошибка", "Не удалось открыть указанный путь.")

    def open_video_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        path = Path("courses") / slug / "input" / "video"
        self.open_path(
            path,
            "Папка не найдена",
            f"Папка с видео не существует:\n{path}",
            f"Открыта папка с видео: {path}",
        )

    def open_audio_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        path = Path("courses") / slug / "input" / "audio"
        self.open_path(
            path,
            "Папка не найдена",
            f"Папка с аудио не существует:\n{path}",
            f"Открыта папка с аудио: {path}",
        )

    def open_prompts_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        path = Path("courses") / slug / "output" / "gpt_prompts"
        self.open_path(
            path,
            "Папка не найдена",
            f"Папка с prompts не существует:\n{path}",
            f"Открыта папка с prompts: {path}",
        )

    def open_summaries_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        path = Path("courses") / slug / "output" / "gpt_summaries"
        self.open_path(
            path,
            "Папка не найдена",
            f"Папка с summaries не существует:\n{path}",
            f"Открыта папка с summaries: {path}",
        )

    def open_reports_folder(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        path = Path("courses") / slug / "output" / "reports"
        self.open_path(
            path,
            "Папка не найдена",
            f"Папка с reports не существует:\n{path}",
            f"Открыта папка с reports: {path}",
        )

    def open_summary_index(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.clear_log()
        self.set_progress_idle()

        index_path = Path("courses") / slug / "output" / "reports" / "summary_index.md"
        if not index_path.is_file():
            warning = "Файл summary_index.md ещё не создан. Сначала выполните 'Собрать индекс'."
            self.log(f"[Предупреждение] {warning}")
            messagebox.showwarning("Файл не найден", warning)
            return

        try:
            os.startfile(str(index_path.resolve()))
            self.set_progress_success()
            self.log(f"[Готово] Открыт файл summary_index.md: {index_path}")
        except Exception as exc:
            self.set_progress_error()
            self.log(f"[Ошибка] Не удалось открыть файл: {exc}")
            messagebox.showerror("Ошибка", "Не удалось открыть summary_index.md.")

    def open_analysis_prompt(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.clear_log()
        self.set_progress_idle()

        prompt_path = Path("courses") / slug / "output" / "gpt_prompts" / "course_analysis_prompt.md"
        if not prompt_path.is_file():
            warning = "Файл course_analysis_prompt.md ещё не создан. Сначала выполните 'Промпт анализа курса'."
            self.log(f"[Предупреждение] {warning}")
            messagebox.showwarning("Файл не найден", warning)
            return

        try:
            os.startfile(str(prompt_path.resolve()))
            self.set_progress_success()
            self.log(f"[Готово] Открыт файл course_analysis_prompt.md: {prompt_path}")
        except Exception as exc:
            self.set_progress_error()
            self.log(f"[Ошибка] Не удалось открыть файл: {exc}")
            messagebox.showerror("Ошибка", "Не удалось открыть course_analysis_prompt.md.")

    def open_obsidian_export(self) -> None:
        slug = self.get_slug()
        if not slug:
            return
        if self.command_running:
            messagebox.showwarning("Ошибка", "Дождитесь завершения текущей команды.")
            return

        self.clear_log()
        self.set_progress_idle()

        export_dir = Path("courses") / slug / "output" / "obsidian_export"
        if not export_dir.is_dir():
            warning = "Папка obsidian_export ещё не создана. Сначала выполните 'Экспорт Obsidian'."
            self.log(f"[Предупреждение] {warning}")
            messagebox.showwarning("Папка не найдена", warning)
            return

        try:
            os.startfile(str(export_dir.resolve()))
            self.set_progress_success()
            self.log(f"[Готово] Открыта папка Obsidian export: {export_dir}")
        except Exception as exc:
            self.set_progress_error()
            self.log(f"[Ошибка] Не удалось открыть папку: {exc}")
            messagebox.showerror("Ошибка", "Не удалось открыть папку obsidian_export.")

    def get_course_video_dir(self, slug: str) -> Path:
        return Path("courses") / slug / "input" / "video"

    def get_course_audio_dir(self, slug: str) -> Path:
        return Path("courses") / slug / "input" / "audio"

    def discover_video_files(self, folder: Path) -> list[Path]:
        return discover_video_files_impl(folder, recursive=False)

    def discover_audio_files(self, folder: Path) -> list[Path]:
        files = [p for p in folder.glob("*") if p.is_file() and is_supported_audio_file(p)]
        files.sort(key=lambda p: str(p).lower())
        return files

    def is_relative_to_safe(self, path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    def ask_process_scope(self, kind: str, count: int) -> Literal["all", "one", "cancel"]:
        title = "\u0418\u0437\u0432\u043b\u0435\u0447\u0435\u043d\u0438\u0435 \u0430\u0443\u0434\u0438\u043e" if kind == "video" else "\u0422\u0440\u0430\u043d\u0441\u043a\u0440\u0438\u0431\u0430\u0446\u0438\u044f"
        kind_label = "\u0432\u0438\u0434\u0435\u043e\u0444\u0430\u0439\u043b\u043e\u0432" if kind == "video" else "\u0430\u0443\u0434\u0438\u043e\u0444\u0430\u0439\u043b\u043e\u0432"
        answer = messagebox.askyesnocancel(
            title,
            f"\u041d\u0430\u0439\u0434\u0435\u043d\u043e {kind_label}: {count}.\n\n\u0414\u0430 - \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c \u0432\u0441\u0435 \u0444\u0430\u0439\u043b\u044b.\n\u041d\u0435\u0442 - \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u043e\u0434\u0438\u043d \u0444\u0430\u0439\u043b.\n\u041e\u0442\u043c\u0435\u043d\u0430 - \u043e\u0442\u043c\u0435\u043d\u0438\u0442\u044c.",
        )
        if answer is True:
            return "all"
        if answer is False:
            return "one"
        return "cancel"

    def transcribe(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        audio_dir = self.get_course_audio_dir(slug)
        if not audio_dir.is_dir():
            messagebox.showwarning(
                "Папка не найдена",
                "Папка input/audio не найдена. Сначала добавьте MP3/audio или выполните 'Извлечь аудио'.",
            )
            return

        audio_files = self.discover_audio_files(audio_dir)
        if not audio_files:
            messagebox.showwarning(
                "Нет файлов",
                "В папке input/audio нет поддерживаемых аудиофайлов.",
            )
            return

        scope = self.ask_process_scope("audio", len(audio_files))
        if scope == "cancel":
            return

        selected_path: Path | None = None
        if scope == "all":
            start_message = "Запуск транскрибации всех аудиофайлов..."
        else:
            selected = filedialog.askopenfilename(
                title="Выберите аудиофайл",
                initialdir=str(audio_dir.resolve()),
                filetypes=[
                    ("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac *.wma"),
                    ("All files", "*.*"),
                ],
            )
            if not selected:
                return
            selected_path = Path(selected)
            if not self.is_relative_to_safe(selected_path, audio_dir) or not (
                selected_path.is_file() and is_supported_audio_file(selected_path)
            ):
                messagebox.showwarning(
                    "Некорректный файл",
                    "Можно выбрать только поддерживаемый аудиофайл внутри input/audio.",
                )
                return
            start_message = f"Запуск транскрибации файла: {selected_path.name}"

        if not self.prepare_action(start_message, is_transcribe=True):
            return

        args = build_module_command("src.course_transcribe", slug)
        if selected_path is not None:
            args.extend(["--file", str(selected_path)])
            self.log(f"Выбранный файл: {selected_path}")
        args.append("--overwrite")
        self.run_command_async(args, "Транскрибация завершена.", "Не удалось выполнить транскрибацию.")

    def extract_audio(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        video_dir = self.get_course_video_dir(slug)
        if not video_dir.is_dir():
            messagebox.showwarning(
                "Папка не найдена",
                "Папка input/video не найдена. Сначала откройте папку курса и поместите видео в input/video.",
            )
            return

        video_files = self.discover_video_files(video_dir)
        if not video_files:
            messagebox.showwarning(
                "Нет файлов",
                "В папке input/video нет поддерживаемых видеофайлов.",
            )
            return

        scope = self.ask_process_scope("video", len(video_files))
        if scope == "cancel":
            return

        selected_path: Path | None = None
        if scope == "all":
            start_message = "Запуск извлечения аудио для всех видео..."
        else:
            selected = filedialog.askopenfilename(
                title="Выберите видеофайл",
                initialdir=str(video_dir.resolve()),
                filetypes=[
                    ("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.wmv *.flv"),
                    ("All files", "*.*"),
                ],
            )
            if not selected:
                return
            selected_path = Path(selected)
            if not self.is_relative_to_safe(selected_path, video_dir) or not discover_video_files_impl(selected_path):
                messagebox.showwarning(
                    "Некорректный файл",
                    "Можно выбрать только поддерживаемый видеофайл внутри input/video.",
                )
                return
            start_message = f"Запуск извлечения аудио для файла: {selected_path.name}"

        if not self.prepare_action(start_message):
            return

        args = build_module_command("src.course_extract_audio", slug)
        if selected_path is not None:
            args.extend(["--file", str(selected_path)])
            self.log(f"Выбранный файл: {selected_path}")
        args.append("--overwrite")
        self.run_command_async(args, "Извлечение аудио завершено.", "Не удалось извлечь аудио из видео.")

    def cleanup(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск очистки курса..."):
            return

        args = build_module_command("src.course_cleanup", slug, "--overwrite")
        self.run_command_async(args, "Очистка завершена.", "Не удалось выполнить очистку.")

    def export_prompts(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск создания промптов..."):
            return

        args = build_module_command("src.course_export_prompts", slug, "--overwrite")
        self.run_command_async(args, "Создание промптов завершено.", "Не удалось создать промпты.")

    def build_index(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск сборки индекса..."):
            return

        args = build_module_command("src.course_build_index", slug, "--overwrite")
        self.run_command_async(args, "Сборка индекса завершена.", "Не удалось собрать индекс.")

    def export_course_analysis_prompt(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск создания промпта анализа курса..."):
            return

        args = build_module_command("src.course_export_analysis_prompt", slug, "--overwrite")
        self.run_command_async(
            args,
            "Промпт анализа курса создан.",
            "Не удалось создать промпт анализа курса.",
        )

    def export_obsidian(self) -> None:
        slug = self.get_slug()
        if not slug:
            return

        if not self.prepare_action("Запуск экспорта Obsidian..."):
            return

        args = build_module_command("src.course_export_obsidian", slug, "--overwrite")
        self.run_command_async(
            args,
            "Экспорт Obsidian завершён.",
            "Не удалось выполнить экспорт Obsidian.",
        )

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
        args = build_module_command(
            "src.import_manual_summary",
            answer_file,
            "--source-transcript",
            str(transcript_path),
            "--output-dir",
            str(output_dir),
            "--overwrite",
        )
        self.run_command_async(args, "Импорт summary завершен.", "Не удалось выполнить импорт summary.")


def main() -> None:
    ensure_app_cwd()
    root = tk.Tk()
    CourseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
