# GPT Course Knowledge Extractor — User Guide

Версия: 0.1.0  
Платформа: Windows / portable build  
Основной режим: manual ChatGPT workflow

## Что делает приложение

GPT Course Knowledge Extractor помогает превращать видео- и аудиокурсы в структурированную локальную базу знаний.

```text
video/audio -> mp3 -> transcript -> cleaned transcript -> ChatGPT prompt -> manual GPT summary -> imported summary -> summary index -> course-level analysis prompt -> Obsidian export
```

Приложение подготавливает материалы, промпты, структуру курса и локальные файлы. ChatGPT-ответы пользователь получает вручную в браузере и затем импортирует обратно в проект.

## Структура курса

Каждый курс хранится отдельно:

```text
courses/<course_slug>/
```

Основные папки:

```text
input/video/              исходные видео
input/audio/              исходные или извлечённые mp3/audio
output/transcripts/       txt-транскрипты
output/markdown/          markdown-транскрипты
output/cleaned/           очищенные txt-транскрипты
output/cleaned_markdown/  очищенные markdown-транскрипты
output/gpt_prompts/       prompt-файлы для ChatGPT
output/gpt_summaries/     импортированные summaries
output/reports/           индексы и отчёты
output/obsidian_export/   Obsidian-ready export
```

## Быстрый старт

1. Запустите приложение.
2. Введите код курса, например `react`.
3. Нажмите **Создать курс**.
4. Нажмите **Открыть папку**.
5. Положите видео в `input/video` или готовые MP3 в `input/audio`.
6. Если добавлены видео, нажмите **Извлечь аудио**.
7. Если файлов несколько, выберите: **Да** — все файлы, **Нет** — один файл, **Отмена** — отменить.
8. Нажмите **Транскрибировать**.
9. Нажмите **Очистить**.
10. Нажмите **Создать промпты**.
11. Откройте prompt, скопируйте его в ChatGPT.
12. Сохраните ответ ChatGPT в `.md` или `.txt`.
13. Нажмите **Импорт summary**.
14. Нажмите **Собрать индекс**.
15. Нажмите **Промпт анализа курса**.
16. При необходимости вставьте course-level prompt в ChatGPT.
17. Нажмите **Экспорт Obsidian**.

## Основные кнопки

### Выбор курса

- **Создать курс** — создаёт workspace курса.
- **Обновить статус** — показывает готовые этапы и следующий шаг.
- **Открыть папку** — открывает папку текущего курса.
- **Инструкция** — показывает краткую подсказку.

### Процесс обработки

- **Извлечь аудио** — конвертирует видео из `input/video` в MP3 в `input/audio`.
- **Транскрибировать** — создаёт расшифровку audio/mp3.
- **Очистить** — применяет cleanup/glossary corrections.
- **Создать промпты** — создаёт prompt-файлы для ChatGPT.
- **Импорт summary** — импортирует сохранённый ответ ChatGPT.
- **Собрать индекс** — создаёт `summary_index.md`.
- **Промпт анализа курса** — создаёт prompt для анализа всего курса.
- **Экспорт Obsidian** — создаёт Obsidian-ready структуру.

### Результаты

- **Открыть video** — `input/video`.
- **Открыть audio** — `input/audio`.
- **Открыть prompts** — `output/gpt_prompts`.
- **Открыть summaries** — `output/gpt_summaries`.
- **Открыть reports** — `output/reports`.
- **Открыть summary_index.md** — индекс summaries.
- **Открыть analysis prompt** — course-level prompt.
- **Открыть Obsidian export** — экспорт для Obsidian.

## Когда можно остановиться

Если нужен один ответ ChatGPT по одному ролику, можно остановиться после:

```text
Создать промпты -> ChatGPT answer
```

Если нужна база знаний курса, продолжайте:

```text
Импорт summary -> Собрать индекс -> Промпт анализа курса -> Экспорт Obsidian
```

## Важные ограничения

Не коммитьте `.env`, `ffmpeg.exe`, видео, MP3, generated outputs, `dist/`, `build/`, `.zip`, `_references/`.
