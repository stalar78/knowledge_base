# Release Checklist

## Pre-build
- Verify `git status` is clean except ignored local artifacts.
- Confirm `.env` is not staged/committed.
- Confirm `tools/ffmpeg/ffmpeg.exe` is not staged/committed.
- Confirm media and generated files are not staged/committed.
- Ensure PyInstaller is installed: `python -m PyInstaller --version`.

## Build
- Run: `packaging\build_windows.bat`
- Verify folder exists: `dist\GPTCourseKnowledgeExtractor\`
- Verify versioned zip exists: `dist\GPTCourseKnowledgeExtractor-v0.1.0-portable.zip`

## Portable smoke test
- Launch `dist\GPTCourseKnowledgeExtractor\START_HERE.bat`
- Confirm GUI title includes version `v0.1.0`
- Create a test course
- Click `Обновить статус`
- Open course folder
- Put a small video into `input/video`
- Extract audio for one selected file
- Confirm no terminal window appears
- Confirm MP3 appears in `input/audio`
- Optionally run transcription on a short MP3

## Release package
- Distribute `dist\GPTCourseKnowledgeExtractor-v0.1.0-portable.zip`
- Do not upload `dist/` and `build/` to Git
- Keep FFmpeg licensing/distribution note in mind
