import os
import subprocess
import tempfile
import wave

import sounddevice as sd
from faster_whisper import WhisperModel
from google import genai

SAMPLE_RATE = 16000
MIC_DEVICE = 0
RECORD_SECONDS = 6

# Gemini
client = genai.Client()
MODEL = "gemini-3.6-flash"

# Whisper
whisper = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8",
)


def speak(text):
    print(f"🔊 Nexus: {text}")
    subprocess.run(["/usr/bin/say", text])


def listen():
    print("\n🎤 Listening...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=MIC_DEVICE,
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

    segments, _ = whisper.transcribe(
        filename,
        language="en",
        vad_filter=True,
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    ).strip()

    os.remove(filename)

    print(f"📝 You: {text}")
    return text


def ask_gemini(text):
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            "You are Nexus, a friendly personal AI assistant. "
            "Answer clearly and naturally. "
            "Keep responses reasonably concise because they will be spoken aloud.\n\n"
            f"User: {text}"
        ),
    )

    return response.text.strip()


print("🤖 Nexus AI voice test is ready.")
speak("Nexus is ready.")

while True:

    text = listen()

    if not text:
        continue

    if "stop nexus" in text.lower():
        speak("Goodbye.")
        break

    answer = ask_gemini(text)

    speak(answer)
