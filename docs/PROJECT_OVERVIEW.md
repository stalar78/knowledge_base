# GPT Course Knowledge Extractor — Project Overview

## Purpose

**GPT Course Knowledge Extractor** is a local-first tool for turning video courses into structured knowledge assets.

The project is designed for courses that are not hosted on YouTube and do not have subtitles. The system extracts or accepts audio, transcribes speech into text, cleans the transcript, and later prepares GPT-ready materials for analysis, summarization, study planning, and Obsidian notes.

## Core Idea

```text
Video course → audio → transcript → cleaned text → GPT analysis → markdown notes → Obsidian / course-specific GPT chat
```

The long-term goal is not only to transcribe courses, but to build a personal learning pipeline that helps decide:

- what is worth studying fully;
- what can be studied partially;
- what is mostly noise;
- what should be converted into permanent notes;
- what should be discussed in a separate GPT chat dedicated to a specific course.

## Why This Project Exists

Many video courses are long, repetitive, and hard to search. A learner may need to spend dozens of hours watching material before discovering whether it contains valuable ideas.

This project solves that problem by converting video courses into text and markdown knowledge artifacts that can be searched, summarized, compared, and analyzed.

## Current Stage

The project is currently at **Stage 1 — Local Single-Audio Transcription**.

Already validated manually:

```text
video → mp3 → faster-whisper → timestamped transcript
```

The proof of concept worked successfully on a short MP3 file.

## Target User Workflow

1. Extract audio from a video file.
2. Put the audio file into the project folder.
3. Run the transcription script.
4. Receive `.txt` and `.md` transcript files.
5. Later: send the transcript to GPT for cleanup, summarization, and course analysis.
6. Later: save final notes into Obsidian.
7. Later: create a separate GPT chat for each course to avoid mixing course contexts.

## Design Principles

- **Local-first processing** where possible.
- **Simple file-based workflow**.
- **Markdown as the main knowledge format**.
- **Separate course contexts** to avoid mixing materials.
- **Incremental automation**: first transcription, then cleanup, then GPT analysis, then course-level intelligence.
- **Readable code and documentation** over overengineering.

## Out of Scope for Stage 1

Stage 1 does not include:

- GPT API integration;
- batch processing of entire courses;
- automatic video-to-audio extraction;
- Obsidian graph generation;
- course usefulness scoring;
- GUI or web interface.

These features belong to later stages.
