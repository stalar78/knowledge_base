# Install and Run on Windows

Версия приложения: 0.1.0

## Portable-режим

Если у вас есть архив:

```text
GPTCourseKnowledgeExtractor-v0.1.0-portable.zip
```

распакуйте его в удобную папку.

## Запуск

Вариант 1:

```text
START_HERE.bat
```

Вариант 2:

```text
GPTCourseKnowledgeExtractor.exe
```

Python для portable-сборки устанавливать не нужно.

## FFmpeg

Для извлечения MP3 из видео нужен `ffmpeg.exe`.

Ожидаемый путь:

```text
tools\ffmpeg\ffmpeg.exe
```

Если файла нет:

1. Скачайте Windows build FFmpeg.
2. Найдите `ffmpeg.exe`.
3. Поместите его в `tools\ffmpeg\ffmpeg.exe`.
4. Не переименовывайте файл.

## Где лежат курсы

Курсы хранятся внутри portable-папки:

```text
courses\<course_slug>\
```

## Первый тест

1. Запустите приложение.
2. Введите код курса `test_course`.
3. Нажмите **Создать курс**.
4. Нажмите **Открыть папку**.
5. Убедитесь, что созданы `input\video`, `input\audio`, `output`.
6. Нажмите **Обновить статус**.
7. Убедитесь, что терминальное окно не появляется, а вывод отображается в GUI.

## Сборка из исходников

```bash
python -m pip install pyinstaller
packaging\build_windows.bat
```

Ожидаемые результаты:

```text
dist\GPTCourseKnowledgeExtractor\
dist\GPTCourseKnowledgeExtractor-v0.1.0-portable.zip
```

## Что не нужно коммитить

```text
dist/
build/
*.exe
*.zip
tools/ffmpeg/ffmpeg.exe
courses/*/input/audio/*
courses/*/input/video/*
courses/*/output/*
.env
_references/
```

## Если не извлекается аудио

Проверьте:

- `ffmpeg.exe` лежит в `tools\ffmpeg\ffmpeg.exe`;
- видео лежит в `courses\<course_slug>\input\video\`;
- в GUI выбран правильный курс.

## Если транскрибация не запускается

Проверьте:

- MP3 лежит в `courses\<course_slug>\input\audio\`;
- выбран правильный курс;
- для длинного аудио CPU-транскрибация может занимать десятки минут.
