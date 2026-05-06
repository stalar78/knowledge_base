from faster_whisper import WhisperModel
from pathlib import Path

audio_path = Path(
    "Сначала смотрим это видео! (online-audio-converter.com).mp3")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

segments, info = model.transcribe(
    str(audio_path),
    language="ru",
    beam_size=5,
    vad_filter=True
)

print(f"Detected language: {info.language}")
print(f"Duration: {info.duration:.2f} seconds")
print()

full_text = []

for segment in segments:
    line = f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text.strip()}"
    print(line)
    full_text.append(line)

output_path = audio_path.with_suffix(".txt")
output_path.write_text("\n".join(full_text), encoding="utf-8")

print()
print(f"Transcript saved to: {output_path}")
