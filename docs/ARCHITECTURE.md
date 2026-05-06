# Architecture

## Current Architecture: Stage 1

Stage 1 focuses on one task only:

```text
single audio file → local transcription → transcript files
```

The system accepts an audio file, transcribes it with `faster-whisper`, prints timestamped segments to the console, and saves the result to the `output/` directory.

## Project Structure

```text
gpt-course-knowledge-extractor/
  input/
    audio/
    video/
  output/
    transcripts/
    markdown/
    reports/
  src/
    transcribe_audio.py
  docs/
    PROJECT_OVERVIEW.md
    ARCHITECTURE.md
    WORKFLOW.md
    ROADMAP.md
    AGENTS.md
  README.md
  requirements.txt
  .gitignore
```

## Directory Responsibilities

### `input/audio/`

Stores audio files prepared for transcription.

Recommended formats:

- `.mp3`
- `.wav`
- `.m4a`
- `.webm`

### `input/video/`

Reserved for original video files.

Stage 1 does not process video directly. Video-to-audio extraction will be added later.

### `output/transcripts/`

Stores raw timestamped transcripts in `.txt` format.

Example:

```text
output/transcripts/lesson_01.txt
```

### `output/markdown/`

Stores markdown transcript files prepared for later GPT analysis or Obsidian import.

Example:

```text
output/markdown/lesson_01.md
```

### `output/reports/`

Reserved for future processing reports:

- transcription quality reports;
- GPT analysis reports;
- course-level summaries;
- error logs;
- usefulness scoring.

### `src/`

Contains Python source code.

Current main script:

```text
src/transcribe_audio.py
```

### `docs/`

Contains project documentation maintained by the Architect.

## Stage 1 Processing Flow

```text
User provides audio file
        ↓
transcribe_audio.py validates path
        ↓
faster-whisper loads local model
        ↓
Audio is transcribed into segments
        ↓
Segments are printed to console
        ↓
TXT transcript is saved
        ↓
Markdown transcript is saved
```

## Transcription Engine

Current planned engine:

```text
faster-whisper
```

Default model:

```text
small
```

Default runtime mode:

```text
CPU + int8
```

Default language:

```text
ru
```

These defaults are chosen because the first real use case is Russian-language course material and the initial goal is reliability on a normal local machine.

## Output Format

The `.txt` file contains timestamped transcript lines.

The `.md` file contains:

```markdown
# Transcript: <audio filename>

## Metadata
- Source file: <path>
- Language: ru
- Duration: <duration> seconds
- Model: small

## Transcript

[00:00:00 - 00:00:05] text...
```

## Future Architecture Direction

Later stages will add additional layers:

```text
Audio/Video Layer
        ↓
Transcription Layer
        ↓
Transcript Cleanup Layer
        ↓
GPT Analysis Layer
        ↓
Course Knowledge Layer
        ↓
Obsidian Export Layer
        ↓
Course-Specific GPT Chat Layer
```

## Architectural Rule

Each stage should be useful on its own.

This means Stage 1 must remain a clean local transcription tool even before GPT integration exists.
