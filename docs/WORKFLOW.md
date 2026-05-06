# Workflow

## Current Workflow: Stage 1

Stage 1 is focused on converting a single audio file into readable transcript files.

```text
audio file → faster-whisper → .txt transcript + .md transcript
```

## Manual Preparation

If the source is a video course, audio should be extracted first.

For the first proof of concept, audio was extracted manually through an online converter.

Later, video-to-audio extraction will be automated with `ffmpeg`.

## Recommended Stage 1 Workflow

### 1. Prepare the audio file

Put the audio file into:

```text
input/audio/
```

Example:

```text
input/audio/lesson_01.mp3
```

### 2. Run transcription

From the project root, run:

```bash
python src/transcribe_audio.py input/audio/lesson_01.mp3
```

On some systems, use:

```bash
py src/transcribe_audio.py input/audio/lesson_01.mp3
```

or:

```bash
python3 src/transcribe_audio.py input/audio/lesson_01.mp3
```

### 3. Check console output

The script should print timestamped segments:

```text
[00:00:00 - 00:00:04] Привет! ...
[00:00:04 - 00:00:09] ...
```

### 4. Check generated files

The script should create:

```text
output/transcripts/lesson_01.txt
output/markdown/lesson_01.md
```

## Later Workflow: GPT Analysis

After transcription is stable, the next step will be:

```text
transcript.md → GPT cleanup → structured lesson note
```

A future GPT analysis output may include:

- short summary;
- detailed summary;
- key ideas;
- practical actions;
- mistakes or questionable claims;
- terminology;
- useful code examples;
- Obsidian-ready note;
- recommendation: study fully, partially, or skip.

## Later Workflow: Full Course Processing

Eventually the workflow should support entire course folders:

```text
input/course_name/audio/
  lesson_01.mp3
  lesson_02.mp3
  lesson_03.mp3
        ↓
batch transcription
        ↓
lesson-level transcripts
        ↓
lesson-level summaries
        ↓
course-level map
        ↓
course-specific GPT chat
```

## Separate GPT Chats for Courses

After the software is created, each course should have its own GPT chat.

Reason:

```text
Do not mix course transcripts, terminology, conclusions, and study decisions from different courses.
```

Recommended pattern:

```text
Main project chat:
  architecture, code, documentation, roadmap, agent management

Course chat #1:
  only Course A transcripts and analysis

Course chat #2:
  only Course B transcripts and analysis
```

## Quality Control

After each transcription, check:

- whether the audio was processed fully;
- whether the language was detected correctly;
- whether important terms were misrecognized;
- whether timestamps are usable;
- whether the markdown output is readable.

Typical Russian transcription corrections may include:

```text
ВПМ → VPN
джепити → GPT
пайтон → Python
джава скрипт → JavaScript
ноутбук лм → NotebookLM
```

These corrections will later become part of the cleanup layer.
