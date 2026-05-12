# Ii Start

This folder contains materials for the course **Ii Start** (`ii_start`).

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
python -m src.transcribe_batch courses/ii_start/input/audio --overwrite
```

### 2. Clean up transcripts

```bash
python -m src.cleanup_transcript courses/ii_start/output/transcripts \
  --output-dir courses/ii_start/output/cleaned \
  --markdown-output-dir courses/ii_start/output/cleaned_markdown \
  --overwrite
```

### 3. Export ChatGPT prompts

```bash
python -m src.gpt_prompt_batch_export courses/ii_start/output/cleaned \
  --output-dir courses/ii_start/output/gpt_prompts \
  --overwrite
```

### 4. Import manual ChatGPT summaries

After copying a prompt into ChatGPT and saving the answer as a local `.md` file:

```bash
python -m src.import_manual_summary manual_answer.md \
  --source-transcript courses/ii_start/output/cleaned/example.txt \
  --output-dir courses/ii_start/output/gpt_summaries \
  --overwrite
```

### 5. Build summary index

```bash
python -m src.build_summary_index courses/ii_start/output/gpt_summaries \
  --output courses/ii_start/output/reports/summary_index.md \
  --json-output courses/ii_start/output/reports/summary_index.json \
  --overwrite
```

## Notes

- All output folders are ignored by Git except `.gitkeep` placeholders.
- You can adjust the paths in the commands to match your actual file names.
- This workflow does **not** call the OpenAI API; it is designed for manual ChatGPT interaction.

