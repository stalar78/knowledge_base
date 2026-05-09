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

### Project status

**Stage 1** – Single‑file transcription is implemented.
**Stage 2** – Batch processing of multiple files is implemented.
**Stage 3** – Transcript cleanup with glossary replacements is implemented.
Planned stages (see `docs/ROADMAP.md`):
- Stage 4: GPT‑based summarization & knowledge extraction
- Stage 5: Interactive web interface

### Notes

- The script uses `faster‑whisper`, a reimplementation of OpenAI's Whisper that is up to 4× faster with lower memory usage.
- On first run, the selected model will be downloaded (cached locally for subsequent runs).
- For long files, transcription may take several minutes on CPU. Consider using `--device cuda` if you have a compatible GPU.
- All output folders are created automatically; you don't need to create them manually.

### License

MIT