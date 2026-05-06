# Roadmap

## Stage 0 — Proof of Concept

Status: completed manually.

Goal:

```text
Check whether audio extracted from a video course can be transcribed successfully.
```

Validated flow:

```text
video → mp3 → faster-whisper → timestamped txt transcript
```

Result:

The proof of concept worked on a short MP3 file.

## Stage 1 — Local Single-Audio Transcription

Status: current stage.

Goal:

```text
Create a clean script that transcribes one audio file and saves .txt and .md outputs.
```

Required features:

- command-line audio path argument;
- `faster-whisper` integration;
- Russian language default;
- CPU + int8 default mode;
- timestamped console output;
- `.txt` transcript output;
- `.md` transcript output;
- automatic output folder creation;
- graceful missing-file errors.

Not included yet:

- GPT API;
- batch processing;
- video-to-audio extraction;
- Obsidian export logic.

## Stage 2 — Batch Audio Processing

Goal:

```text
Process a folder with many audio lessons automatically.
```

Planned features:

- input folder argument;
- supported audio file discovery;
- one transcript per lesson;
- progress reporting;
- skip already processed files;
- basic error report.

## Stage 3 — Transcript Cleanup and Normalization

Goal:

```text
Clean raw transcripts before GPT analysis.
```

Planned features:

- remove filler phrases when safe;
- normalize repeated words;
- fix common recognition mistakes;
- apply custom dictionary;
- preserve timestamps;
- create cleaned markdown output.

Examples:

```text
ВПМ → VPN
джепити → GPT
пайтон → Python
джава скрипт → JavaScript
```

## Stage 4 — GPT Lesson Analysis

Goal:

```text
Turn each cleaned transcript into useful learning materials.
```

Planned outputs:

- short lesson summary;
- detailed lesson summary;
- key ideas;
- practical steps;
- terminology;
- code examples if present;
- questionable claims;
- Obsidian-ready note;
- study recommendation.

Possible study verdicts:

```text
Study fully
Study partially
Use as reference
Skip
```

## Stage 5 — Course-Level Analysis

Goal:

```text
Analyze the entire course as one knowledge object.
```

Planned outputs:

- course map;
- module structure;
- repeated ideas;
- most valuable lessons;
- weak or redundant lessons;
- learning path;
- practical project checklist;
- overall usefulness score.

## Stage 6 — Course-Specific GPT Chats

Goal:

```text
Keep each course in a separate GPT chat after software processing is complete.
```

Purpose:

- avoid mixing course contexts;
- keep terminology clean;
- preserve course-specific analysis;
- allow deep discussion of one course at a time.

Recommended structure:

```text
Main project chat:
  development and architecture

Course chat:
  one specific course only
```

## Stage 7 — Obsidian Knowledge Export

Goal:

```text
Export GPT analysis into a clean Obsidian vault structure.
```

Planned outputs:

```text
ObsidianVault/
  Courses/
    CourseName/
      00_Course_Map.md
      01_Lesson_Notes/
      02_Key_Ideas/
      03_Practical_Tasks/
      04_Terms/
      05_Final_Review.md
```

## Stage 8 — Personal Knowledge Relevance Scoring

Goal:

```text
Estimate how useful a course is for the user personally.
```

Potential scoring dimensions:

- novelty;
- practical value;
- relation to current projects;
- depth;
- redundancy;
- implementation usefulness;
- time-to-value.

## Roadmap Rule

Do not jump to GPT automation too early.

The local transcription pipeline must be stable first.
