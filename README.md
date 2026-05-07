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

### Project status

**Stage 1** – Single‑file transcription is implemented.  
Planned stages (see `docs/ROADMAP.md`):
- Stage 2: Batch processing of multiple files
- Stage 3: Video‑to‑audio extraction
- Stage 4: GPT‑based summarization & knowledge extraction
- Stage 5: Interactive web interface

### Notes

- The script uses `faster‑whisper`, a reimplementation of OpenAI's Whisper that is up to 4× faster with lower memory usage.
- On first run, the selected model will be downloaded (cached locally for subsequent runs).
- For long files, transcription may take several minutes on CPU. Consider using `--device cuda` if you have a compatible GPU.
- All output folders are created automatically; you don't need to create them manually.

### License

MIT