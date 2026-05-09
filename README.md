# GPT Course Knowledge Extractor

A Python tool for extracting structured knowledge from educational audio/video content using automatic transcription and GPT‑based analysis.

## Stage 1: Single‑file transcription with faster‑whisper

This stage provides a clean, beginner‑friendly script that transcribes a single audio file into plain text and markdown with timestamps.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/stalar78/knowledge_base.git
   cd knowledge_base
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # on Windows
   # source .venv/bin/activate # on Linux/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Preparing audio files

Place your audio files (MP3, WAV, M4A, FLAC, etc.) into the `input/audio/` folder.  
You can also place video files into `input/video/` (video‑to‑audio extraction will be added in a later stage).

The folder structure is created automatically when you run the script for the first time.

### Running the transcription script

You can run the script in two equivalent ways:

**1. Direct script execution** (traditional):
```bash
python src/transcribe_audio.py input/audio/my_lecture.mp3
```

**2. Module execution** (recommended, more robust):
```bash
python -m src.transcribe_audio input/audio/my_lecture.mp3
```

Both styles accept the same arguments.

Optional arguments:
- `--model` – Whisper model size (`tiny`, `base`, `small`, `medium`, `large‑v2`). Default: `small`
- `--language` – Language code (`ru`, `en`, `auto`). Default: `ru`
- `--device` – Inference device (`cpu`, `cuda`, `auto`). Default: `cpu`
- `--compute-type` – Quantization type (`int8`, `float16`, `float32`). Default: `int8`
- `--overwrite` – Overwrite existing output files (default: skip if outputs exist)

Example with custom parameters:
```bash
python -m src.transcribe_audio input/audio/lecture.wav --model medium --language en --device cpu --compute-type float16
```

### Supported input formats

The script accepts the following audio/video file extensions (via faster‑whisper/ffmpeg):

- **Audio:** `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`
- **Video containers (audio stream will be extracted):** `.webm`, `.mp4`, `.mkv`, `.mov`, `.avi`

If you provide a file with an unsupported extension, the script will print an error and exit.

### Smoke test

To quickly verify the installation and basic functionality, you can run:

```bash
python src/transcribe_audio.py input/audio/test.mp3 --overwrite
```

(Ensure you have a test file at that location, or create a short dummy audio file.)

### Output files

The script creates two transcript files:

1. **Plain text** – `output/transcripts/<filename>.txt`  
   Contains timestamps and raw transcript lines.

2. **Markdown** – `output/markdown/<filename>.md`  
   Includes metadata (source, language, duration, model settings) and the formatted transcript.

Example markdown structure:
```markdown
# Transcript: lecture.mp3

## Metadata
- Source file: `C:\...\input\audio\lecture.mp3`
- Language: `ru`
- Duration: `125.34` seconds
- Model: `small`
- Device: `cpu`
- Compute type: `int8`

## Transcript
[00:00:00 - 00:00:05] Hello, welcome to today's lecture...
```

## Stage 2: Batch transcription

This stage adds a batch‑processing script that transcribes all supported audio/video files in a folder (optionally recursively) with a single model load.

### Running batch transcription

You can run the batch script in the same two ways:

**1. Direct script execution:**
```bash
python src/transcribe_batch.py input/audio
```

**2. Module execution (recommended):**
```bash
python -m src.transcribe_batch input/audio
```

### Additional options

All options from the single‑file script are supported, plus:

- `--recursive` – scan subfolders recursively (default: only top‑level folder)
- `--overwrite` – overwrite existing output files (default: skip files that already have outputs)

### Examples

Transcribe all supported files in `input/audio` (non‑recursive):
```bash
python -m src.transcribe_batch input/audio
```

Scan recursively and overwrite any existing transcripts:
```bash
python -m src.transcribe_batch input/audio --recursive --overwrite
```

Use a larger model and English language:
```bash
python -m src.transcribe_batch input/audio --model medium --language en
```

### How it works

1. The script scans the specified folder (and its subfolders if `--recursive` is used) for files with supported extensions (see Stage 1 for the list).
2. The Whisper model is loaded **once** and reused for all files, which greatly speeds up processing.
3. For each file:
   - If output files already exist and `--overwrite` is not given, the file is skipped with a clear message.
   - Otherwise, transcription is performed and plain‑text/markdown transcripts are saved to `output/transcripts/` and `output/markdown/` (same naming convention as Stage 1).
4. A progress counter `[index/total]` is printed for each file.
5. At the end, a summary shows how many files were processed, skipped, or failed.

### Notes

- The script uses the same helper functions (`ensure_output_dirs`, `get_output_paths`, `format_timestamp`, `is_supported_audio_file`) as the single‑file script, ensuring consistent output structure.
- If a transcription fails for one file, the error is printed and the script continues with the next file.
- If no supported files are found, the script exits with a clear message.
- The transcription logic is shared between the single‑file and batch scripts via `src/transcription_engine.py`.

## Stage 3: Transcript cleanup

This stage adds a local glossary‑based cleanup of transcript files, correcting common mis‑transcriptions (e.g., “джипити” → “GPT”) without using GPT API.

### Running transcript cleanup

You can run the cleanup script in the same two ways:

**1. Direct script execution:**
```bash
python src/cleanup_transcript.py output/transcripts/test.txt --overwrite
```

**2. Module execution (recommended):**
```bash
python -m src.cleanup_transcript output/transcripts/test.txt --overwrite
```

### Additional options

- `--glossary` – path to JSON glossary file (default: `config/glossary_replacements.json`)
- `--output-dir` – directory for cleaned plain‑text transcripts (default: `output/cleaned`)
- `--markdown-output-dir` – directory for cleaned markdown transcripts (default: `output/cleaned_markdown`)
- `--recursive` – scan subfolders recursively (only when input is a folder)
- `--overwrite` – overwrite existing cleaned output files

### Examples

Clean a single transcript file:
```bash
python -m src.cleanup_transcript output/transcripts/test.txt --overwrite
```

Clean all `.txt` files in a folder (non‑recursive):
```bash
python -m src.cleanup_transcript output/transcripts --overwrite
```

Clean recursively and overwrite any existing cleaned outputs:
```bash
python -m src.cleanup_transcript output/transcripts --recursive --overwrite
```

### How it works

1. The script loads a replacement dictionary from `config/glossary_replacements.json` (you can edit this file to add your own replacements).
2. It scans the input path (single file or folder) for `.txt` transcript files.
3. For each file:
   - If cleaned outputs already exist and `--overwrite` is not given, the file is skipped.
   - Otherwise, the script reads the transcript, applies all glossary replacements (case‑sensitive, longest‑first), and counts how many replacements were made.
   - It saves the cleaned plain‑text transcript to `output/cleaned/<filename>.txt`.
   - It also generates a markdown version with metadata (source, glossary, replacement count) in `output/cleaned_markdown/<filename>.md`.
4. A progress counter `[index/total]` is printed for each file.
5. At the end, a summary shows how many files were processed, skipped, or failed.

### Audit reports

Starting from Stage 3.1, the cleanup script generates detailed audit reports in JSON and Markdown formats. These reports track exactly which replacements were applied, how many times each replacement occurred, and provide a file‑by‑file breakdown.

#### Report location

After each run, two report files are created in `output/reports/`:

- `cleanup_report.json` – structured JSON with full statistics and replacement details.
- `cleanup_report.md` – human‑readable Markdown summary with tables.

#### JSON report structure

```json
{
  "processed": 2,
  "skipped": 0,
  "failed": 0,
  "total_replacements": 8,
  "files": [
    {
      "input": "output/transcripts/test1.txt",
      "status": "processed",
      "replacements": 4,
      "details": {"джипити -> GPT": 2, "ВПМ -> VPN": 2}
    }
  ],
  "global_replacements": {"джипити -> GPT": 4, "ВПМ -> VPN": 4}
}
```

#### Markdown report contents

The Markdown report includes:

- **Summary table** – counts of processed, skipped, failed files and total replacements.
- **File‑level table** – each file’s status, replacement count, and a link to the cleaned output.
- **Global replacements table** – aggregated counts of each replacement across all files.
- **Execution details** – timestamp, glossary path, command‑line arguments.

#### How to view reports

You can open the reports directly after a cleanup run:

```bash
# View JSON report (requires jq for pretty‑printing)
jq . output/reports/cleanup_report.json

# View Markdown report
cat output/reports/cleanup_report.md
```

Reports are overwritten on each script run. If you need to keep historical reports, move or rename them manually.

### Notes

- The glossary is a simple JSON object `{"mis‑transcribed": "correct", …}`. You can edit it at any time.
- This stage is completely local and does not require an internet connection or GPT API.
- The script uses the same helper `ensure_output_dirs` to create output folders automatically.

## Stage 4.0: OpenAI configuration

This stage prepares the project for future GPT‑based summarization by adding a configuration layer and a minimal OpenAI client wrapper. No API calls are made yet.

### Configuration files

- **`.env.example`** – template for environment variables. Copy it to `.env` and add your OpenAI API key:
  ```bash
  cp .env.example .env
  ```
  Then edit `.env` and set:
  ```
  OPENAI_API_KEY=your_openai_api_key_here
  ```
  The `.env` file is ignored by Git (see `.gitignore`).

- **`config/openai_settings.json`** – contains model parameters (model name, temperature, max tokens). You can adjust these values before running future summarization scripts.

### Dependencies

The `openai` package has been added to `requirements.txt`. Install it with:
```bash
pip install -r requirements.txt
```

### Smoke check

To verify that your configuration is correctly loaded, run:
```bash
python -m src.gpt_client
```
This command will:
- Load the `.env` file (if present).
- Load settings from `config/openai_settings.json`.
- Check that `OPENAI_API_KEY` is set.
- Print the loaded model and parameters.

If the API key is missing, you’ll see a clear error message explaining how to fix it.

### What’s next?

The `src/gpt_client.py` module provides a function `get_openai_client_and_settings()` that returns a ready‑to‑use OpenAI client and the settings dictionary. This will be used in Stage 4.1 (actual summarization) without requiring additional configuration.

**Important:** This stage does **not** call the OpenAI API yet. It only sets up the configuration and validation layer.

## Stage 4.1: GPT summary for one transcript

This stage adds a script that calls the OpenAI API to generate a structured markdown summary of a cleaned transcript file.

### Requirements

- A valid `.env` file with `OPENAI_API_KEY` (see Stage 4.0).
- A cleaned transcript `.txt` file (e.g., from `output/cleaned/`).

### Usage

```bash
python -m src.gpt_summarize output/cleaned/test.txt --overwrite
```

Optional arguments:
- `--output-dir` – directory where the summary markdown file will be saved (default: `output/gpt_summaries/`).
- `--overwrite` – overwrite existing summary file (default: skip if exists).

### Output

The script creates a markdown file in `output/gpt_summaries/` with the same stem as the input file, e.g.:

```
output/gpt_summaries/test.md
```

The file contains:

- **Metadata** (source file, model, temperature, max tokens).
- **GPT‑generated sections**:
  - Short Summary
  - Key Ideas
  - Practical Actions
  - Important Terms
  - Noise / Low‑value Content
  - Study Recommendation

### Notes

- This stage **calls the OpenAI API** and may incur API costs.
- The prompt is designed for educational transcripts; you can adjust it in `src/gpt_summarize.py`.
- The script validates input file existence and extension, and skips existing outputs unless `--overwrite` is used.

### Stage 4.1 Manual mode: ChatGPT prompt export

When OpenAI API quota is not available, you can use this manual fallback mode. It exports a ready‑to‑copy ChatGPT prompt that you can paste into the ChatGPT web interface (or app) and manually save the answer.

#### Requirements

- No `.env` or `OPENAI_API_KEY` required.
- A cleaned transcript `.txt` file (e.g., from `output/cleaned/`).

#### Usage

```bash
python -m src.gpt_prompt_export output/cleaned/test.txt --overwrite
```

Optional arguments:
- `--output-dir` – directory where the prompt markdown file will be saved (default: `output/gpt_prompts/`).
- `--overwrite` – overwrite existing prompt file (default: skip if exists).

#### Output

The script creates a markdown file in `output/gpt_prompts/` with the suffix `_prompt.md`, e.g.:

```
output/gpt_prompts/test_prompt.md
```

The file contains a complete ChatGPT prompt that includes the transcript and asks for the same six‑section summary as the API version.

#### Manual workflow

1. Copy the entire content of the prompt file.
2. Paste it into ChatGPT (web interface or app).
3. Copy ChatGPT's answer.
4. Save the answer manually to `output/gpt_summaries/<input_stem>.md`.

#### Notes

- This mode **does not call the OpenAI API** and does not require an API key.
- The generated prompts are ignored by Git (see `.gitignore`).
- You can reuse the same prompt with different ChatGPT models (GPT‑3.5, GPT‑4, etc.).

### Stage 4.2: Batch manual prompt export

This stage adds a batch‑processing script that exports ready‑to‑copy ChatGPT prompts for **all** cleaned transcript files in a folder (optionally recursively). It is the batch counterpart of Stage 4.1‑manual.

#### Requirements

- No `.env` or `OPENAI_API_KEY` required.
- A folder containing cleaned transcript `.txt` files (e.g., `output/cleaned/`).

#### Usage

```bash
python -m src.gpt_prompt_batch_export output/cleaned --overwrite
```

Optional arguments:
- `--output-dir` – directory where prompt markdown files will be saved (default: `output/gpt_prompts/`).
- `--recursive` – search for `.txt` files recursively in subfolders.
- `--overwrite` – overwrite existing prompt files (default: skip if exists).

Recursive example:
```bash
python -m src.gpt_prompt_batch_export output/cleaned --recursive --overwrite
```

#### Output

For each `.txt` file found, the script creates a markdown prompt file in `output/gpt_prompts/` with the suffix `_prompt.md`, e.g.:

```
output/gpt_prompts/lesson_01_prompt.md
output/gpt_prompts/lesson_02_prompt.md
```

Each file contains a complete ChatGPT prompt that includes the transcript and asks for the same six‑section summary as the API version.

#### Reporting

The script prints:
- Number of discovered transcript files.
- Progress: `[1/5] Exported prompt for lesson_01.txt`
- Final summary: exported, skipped, and failed counts.

#### Notes

- This mode **does not call the OpenAI API** and does not require an API key.
- The generated prompts are ignored by Git (see `.gitignore`).
- You can reuse the same prompts with different ChatGPT models (GPT‑3.5, GPT‑4, etc.).

### Stage 4.3: Manual summary import

This stage completes the manual workflow by providing a clean way to import/save ChatGPT's markdown answer into the standard summary directory (`output/gpt_summaries/`) with consistent metadata.

#### Purpose

After you copy a generated prompt into ChatGPT manually, you need to store ChatGPT's answer in a structured format. This script imports the answer file, adds metadata (source transcript, import mode, etc.), and saves it as a standardized markdown summary.

#### Requirements

- No `.env` or `OPENAI_API_KEY` required.
- A markdown/text file containing ChatGPT's answer (e.g., `manual_answer.md`).
- The original cleaned transcript `.txt` file (used for naming and metadata).

#### Usage

```bash
python -m src.import_manual_summary manual_answer.md --source-transcript output/cleaned/test.txt --overwrite
```

Optional arguments:
- `--output-dir` – directory where the imported summary will be saved (default: `output/gpt_summaries/`).
- `--overwrite` – overwrite existing summary file (default: skip if exists).

#### Workflow example

1. **Generate a prompt** (single file):
   ```bash
   python -m src.gpt_prompt_export output/cleaned/test.txt --overwrite
   ```
   This creates `output/gpt_prompts/test_prompt.md`.

2. **Copy the prompt** into ChatGPT (web interface or app).

3. **Save ChatGPT's answer** locally, for example as `manual_answer.md`.

4. **Import the answer**:
   ```bash
   python -m src.import_manual_summary manual_answer.md --source-transcript output/cleaned/test.txt --overwrite
   ```

5. **Final summary** appears at:
   ```
   output/gpt_summaries/test.md
   ```

#### Output format

The imported summary file contains:

```markdown
# GPT Summary: test.txt

## Metadata

- Source transcript: /full/path/to/output/cleaned/test.txt
- Manual answer file: /full/path/to/manual_answer.md
- Import mode: manual ChatGPT
- Notes: Imported from a manually copied ChatGPT answer.

---

<content of answer_file>
```

#### Notes

- This mode **does not call the OpenAI API** and does not require an API key.
- Generated summaries in `output/gpt_summaries/` are ignored by Git (see `.gitignore`).
- The script validates that both input files exist and have the correct extensions (`.md` for answer, `.txt` for transcript).
- If the output file already exists and `--overwrite` is not passed, the script prints a skip message and exits cleanly.

### Stage 4.4: Summary index

This stage builds a local index/catalog from imported GPT summary markdown files. After you have imported several manual ChatGPT summaries into `output/gpt_summaries/`, you can generate a simple index that lists available summaries and extracts basic metadata for later course‑level analysis.

#### Purpose

Create a human‑readable markdown table and a machine‑readable JSON file that catalog all summary files, their titles, source transcripts, and approximate word counts. The index is generated locally and does not call the OpenAI API.

#### Requirements

- No `.env` or `OPENAI_API_KEY` required.
- A folder containing imported summary `.md` files (e.g., `output/gpt_summaries/`).

#### Usage

```bash
python -m src.build_summary_index output/gpt_summaries --overwrite
```

Optional arguments:
- `--output` – markdown output file (default: `output/reports/summary_index.md`).
- `--json-output` – JSON output file (default: `output/reports/summary_index.json`).
- `--recursive` – search for `.md` files recursively in subfolders.
- `--overwrite` – overwrite existing index files (default: skip if exists).

#### Output

The script creates two files in `output/reports/`:

1. **Markdown index** – `summary_index.md`
   Contains a table with columns: #, Summary file, Title, Source transcript, Words.

   Example:
   ```markdown
   # Summary Index

   ## Summary

   - Summary files: 2

   ## Files

   | # | Summary file | Title | Source transcript | Words |
   |---:|:---|:---|:---|:---:|
   | 1 | output/gpt_summaries/test.md | GPT Summary: test.txt | output/cleaned/test.txt | 350 |
   ```

2. **JSON index** – `summary_index.json`
   Structured data with the same information for programmatic use.

   Example:
   ```json
   {
     "summary_count": 1,
     "files": [
       {
         "summary_file": "output/gpt_summaries/test.md",
         "title": "GPT Summary: test.txt",
         "source_transcript": "...",
         "manual_answer_file": "...",
         "import_mode": "manual ChatGPT",
         "word_count": 350
       }
     ]
   }
   ```

#### Metadata extraction

The script reads each `.md` file and extracts:
- **Title** from the first `#` heading.
- **Source transcript**, **Manual answer file**, **Import mode** from the “## Metadata” section (if present).
- **Word count** (approximate, based on whitespace splitting).

If a metadata field is missing, it is stored as an empty string.

#### Notes

- This mode **does not call the OpenAI API** and does not require an API key.
- Generated index files are ignored by Git (see `.gitignore` rule `output/reports/*`).
- The script validates the input directory, skips missing files, and exits cleanly when no `.md` files are found.

### Project status

**Stage 1** – Single‑file transcription is implemented.
**Stage 2** – Batch processing of multiple files is implemented.
**Stage 3** – Transcript cleanup with glossary replacements is implemented.
**Stage 4.0** – OpenAI configuration layer is implemented.
**Stage 4.1** – GPT‑based summarization for a single transcript is implemented.
**Stage 4.1‑manual** – ChatGPT prompt export for manual summarization is implemented.
**Stage 4.2** – Batch manual prompt export is implemented.
**Stage 4.3** – Manual summary import is implemented.
**Stage 4.4** – Summary index is implemented.
Planned stages (see `docs/ROADMAP.md`):
- Stage 5: Interactive web interface

### Notes

- The script uses `faster‑whisper`, a reimplementation of OpenAI's Whisper that is up to 4× faster with lower memory usage.
- On first run, the selected model will be downloaded (cached locally for subsequent runs).
- For long files, transcription may take several minutes on CPU. Consider using `--device cuda` if you have a compatible GPU.
- All output folders are created automatically; you don't need to create them manually.

### License

MIT