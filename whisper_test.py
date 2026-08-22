import sounddevice as sd
import wave
import tempfile
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
DURATION = 6

print("🎤 Nexon is listening...")
print("Speak now!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=0
)
sd.wait()

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    filename = f.name

with wave.open(filename, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(audio.tobytes())

print("🧠 Whisper is processing...")

model = WhisperModel("base.en", device="cpu", compute_type="int8")

segments, info = model.transcribe(filename)

text = " ".join(segment.text.strip() for segment in segments)

print()
print("Nexon heard:")
print(text)
