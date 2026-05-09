# Test Course 01

This folder contains materials for the course **Test Course 01** (`test_course_01`).

## Folder structure

- `input/audio/` – place audio files for transcription.
- `input/video/` – place video files (audio will be extracted).
- `output/transcripts/` – raw transcript files.
- `output/markdown/` – formatted transcripts with metadata.
- `output/cleaned/` – cleaned transcript text files.
- `output/cleaned_markdown/` – cleaned transcripts in markdown format.
- `output/gpt_prompts/` – ready‑to‑copy ChatGPT prompts.
- `output/gpt_summaries/` – imported ChatGPT summaries.
- `output/reports/` – audit reports and summary index.

## Suggested workflow

### 1. Transcribe audio/video files

```bash
python -m src.transcribe_batch courses/test_course_01/input/audio --overwrite
```

### 2. Clean up transcripts

```bash
python -m src.cleanup_transcript courses/test_course_01/output/transcripts \
  --output-dir courses/test_course_01/output/cleaned \
  --markdown-output-dir courses/test_course_01/output/cleaned_markdown \
  --overwrite
```

### 3. Export ChatGPT prompts

```bash
python -m src.gpt_prompt_batch_export courses/test_course_01/output/cleaned \
  --output-dir courses/test_course_01/output/gpt_prompts \
  --overwrite
```

### 4. Import manual ChatGPT summaries

After copying a prompt into ChatGPT and saving the answer as a local `.md` file:

```bash
python -m src.import_manual_summary manual_answer.md \
  --source-transcript courses/test_course_01/output/cleaned/example.txt \
  --output-dir courses/test_course_01/output/gpt_summaries \
  --overwrite
```

### 5. Build summary index

```bash
python -m src.build_summary_index courses/test_course_01/output/gpt_summaries \
  --output courses/test_course_01/output/reports/summary_index.md \
  --json-output courses/test_course_01/output/reports/summary_index.json \
  --overwrite
```

## Notes

- All output folders are ignored by Git except `.gitkeep` placeholders.
- You can adjust the paths in the commands to match your actual file names.
- This workflow does **not** call the OpenAI API; it is designed for manual ChatGPT interaction.

