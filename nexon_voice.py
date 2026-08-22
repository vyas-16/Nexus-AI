import os
import subprocess
import sounddevice as sd
import wave
import tempfile
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
DURATION = 6

print("🤖 Nexon command mode")
print("🎤 Speak a command...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=0,
)
sd.wait()

with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
    filename = f.name

with wave.open(filename, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(SAMPLE_RATE)
    wav.writeframes(audio.tobytes())

print("🧠 Understanding...")

model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8",
)

segments, _ = model.transcribe(filename)

command = " ".join(
    segment.text.strip() for segment in segments
).lower().strip()

os.remove(filename)

print(f"📝 Nexon heard: {command}")

# ---- SAFE ALLOWLISTED COMMANDS ----

if "spotify" in command and ("open" in command or "launch" in command):
    print("🎵 Opening Spotify...")
    subprocess.Popen(["open", "-a", "Spotify"])
    subprocess.Popen(["/usr/bin/say", "Spotify is open."])

elif "cursor" in command and ("open" in command or "launch" in command):
    print("💻 Opening Cursor...")
    subprocess.Popen(["open", "-a", "Cursor"])
    subprocess.Popen(["/usr/bin/say", "Opening Cursor."])

elif "safari" in command and ("open" in command or "launch" in command):
    print("🌐 Opening Safari...")
    subprocess.Popen(["open", "-a", "Safari"])
    subprocess.Popen(["/usr/bin/say", "Opening Safari."])

elif "stop" in command and ("nexon" in command or "assistant" in command):
    subprocess.Popen(["/usr/bin/say", "Goodbye."])
    print("🛑 Nexon stopping.")

else:
    subprocess.Popen([
        "/usr/bin/say",
        "I heard you, but that command is not available yet."
    ])
    print("⚠️ Command not in the safe allowlist.")
