# GPT Course Knowledge Extractor — Project Status

Актуальная версия: 0.1.0  
Текущий статус: рабочая Windows portable-сборка готова для внутреннего релиза.

## Назначение проекта

Windows-приложение для превращения видео- и аудиокурсов в структурированную базу знаний.

```text
video/audio -> mp3 -> transcript -> cleaned transcript -> ChatGPT prompt -> manual GPT summary -> imported summary -> summary index -> course-level analysis prompt -> Obsidian export
```

## Закрытые этапы

- Stage 0 — PoC.
- Stage 1 — single audio transcription.
- Stage 1.1 — utilities/refactor.
- Stage 2 — batch transcription.
- Stage 2.1 — shared transcription engine.
- Stage 3 — transcript cleanup / glossary corrections.
- Stage 3.1 — cleanup audit reports.
- Stage 4.0 — OpenAI configuration layer.
- Stage 4.1 — API GPT summary реализован, smoke-test блокировался квотой OpenAI.
- Stage 4.1-manual — manual ChatGPT prompt export.
- Stage 4.2 — batch manual prompt export.
- Stage 4.3 — manual summary import.
- Stage 4.4 — summary index builder.
- Stage 5.0 — course workspace initializer.
- Stage 5.1 — course workflow status helper.
- Stage 5.2 — course-aware workflow wrappers.
- Stage 5.3 — console app launcher.
- Stage 5.4 — Windows launcher scripts.
- Stage 6.0 — Tkinter desktop GUI prototype.
- Stage 6.1 — video-to-MP3 extraction.
- Stage 6.2 — GUI results viewer.
- Stage 6.3 — course-level analysis manual mode.
- Stage 6.4 — Obsidian export.
- Stage 6.5 — GUI layout stabilization.
- Stage 7.0 — Windows portable packaging scaffold.
- Stage 7.0.1 — selective file processing.
- Stage 7.0.2 — real PyInstaller build verification.
- Stage 7.0.3 — console hiding attempt.
- Stage 7.0.4 — windowed runner + file logs.
- Stage 7.0.5 — in-process packaged command execution.
- Stage 7.1 — portable distribution cleanup.
- Stage 7.2 — release validation / versioning.

## Ключевые файлы

GUI:

```text
src/gui_app.py
```

Packaging:

```text
src/version.py
src/runtime_environment.py
src/frozen_module_runner.py
packaging/build_windows.bat
packaging/GPTCourseKnowledgeExtractor.spec
packaging/GPTCourseKnowledgeRunner.spec
packaging/templates/START_HERE.bat
packaging/templates/README_PORTABLE.txt
packaging/templates/README_FFMPEG.txt
packaging/RELEASE_CHECKLIST.md
```

Course workflow:

```text
src/create_course_workspace.py
src/course_workflow_status.py
src/course_paths.py
src/course_extract_audio.py
src/course_transcribe.py
src/course_cleanup.py
src/course_export_prompts.py
src/import_manual_summary.py
src/course_build_index.py
src/course_export_analysis_prompt.py
src/course_export_obsidian.py
```

## Portable build

```bash
packaging\build_windows.bat
```

Expected outputs:

```text
dist\GPTCourseKnowledgeExtractor\
dist\GPTCourseKnowledgeExtractor-v0.1.0-portable.zip
```

## Runtime decision

In source mode, GUI may use subprocess-based module execution.

In packaged/frozen mode, GUI runs internal modules in-process with `runpy.run_module(...)` inside a worker thread. This prevents Windows terminal windows from appearing during GUI actions.

## Security / repo rules

Never commit:

```text
.env
tools/ffmpeg/ffmpeg.exe
dist/
build/
*.exe
*.zip
*.mp3
*.mp4
courses/*/input/audio/*
courses/*/input/video/*
courses/*/output/*
output/*
manual_answer*.md
manual_answer*.txt
_references/
```

## Recommended next stages

- Stage 8.1 — documentation integration.
- Stage 8.2 — first internal release.
- Stage 8.3 — real course validation.
- Stage 8.4 — UX polish.
- Stage 8.5 — Obsidian enhancements.
