# Manual ChatGPT Workflow

## Назначение

Документ описывает ручную работу с ChatGPT внутри проекта GPT Course Knowledge Extractor.

```text
приложение готовит prompt -> пользователь вставляет его в ChatGPT -> пользователь сохраняет ответ -> приложение импортирует summary
```

Этот режим не требует OpenAI API key.

## Lesson-level summary workflow

После этапов:

```text
Извлечь аудио -> Транскрибировать -> Очистить
```

нажмите:

```text
Создать промпты
```

Prompt-файлы появятся в:

```text
courses/<course_slug>/output/gpt_prompts/
```

Откройте папку через кнопку **Открыть prompts**, скопируйте prompt в ChatGPT и получите ответ.

## Как сохранить ответ ChatGPT

Сохраните ответ в `.md` или `.txt`, например:

```text
lesson_01_summary.md
```

Затем нажмите **Импорт summary**.

Импортированные summaries попадут в:

```text
courses/<course_slug>/output/gpt_summaries/
```

## Сборка индекса

После импорта summaries нажмите **Собрать индекс**.

Будет создан:

```text
courses/<course_slug>/output/reports/summary_index.md
```

## Course-level analysis prompt

После индекса нажмите **Промпт анализа курса**.

Будет создан:

```text
courses/<course_slug>/output/gpt_prompts/course_analysis_prompt.md
```

Откройте его через **Открыть analysis prompt** и скопируйте в ChatGPT.

## Что должен дать course-level analysis

Course-level prompt просит ChatGPT построить:

- overview курса;
- карту знаний;
- ключевые темы и концепты;
- lesson-by-lesson synthesis;
- связи между уроками;
- повторяющиеся идеи;
- практические действия;
- термины и определения;
- пробелы и вопросы;
- план повторения;
- Obsidian-ready структуру.

## Anti-hallucination rule

Prompt запрещает выдумывать факты за пределами предоставленных summaries. Неясные места должны помечаться как:

```text
needs verification
```

## Obsidian export

После summaries, index и course-level prompt нажмите **Экспорт Obsidian**.

Результат:

```text
courses/<course_slug>/output/obsidian_export/
```

Основные файлы:

```text
00_Course_Home.md
01_Summary_Index.md
02_Course_Analysis_Prompt.md
Lessons/
Source/
_meta/export_manifest.json
```

## Практический режим для большого курса

1. Обрабатывайте один урок или несколько уроков.
2. Делайте prompt.
3. Получайте summary в ChatGPT.
4. Импортируйте summary.
5. Повторяйте.
6. В конце соберите индекс, course-level prompt и Obsidian export.
