import os
import subprocess
import tempfile
import wave
import time

import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
MIC_DEVICE = 0
RECORD_SECONDS = 5

model = WhisperModel(
    "base.en",
    device="cpu",
    compute_type="int8",
)


def speak(text):
    # Give the microphone time to settle before/after Nexon speaks.
    subprocess.run(["/usr/bin/say", text])
    time.sleep(1.0)


def record_command():
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

    segments, _ = model.transcribe(
        filename,
        language="en",
        vad_filter=True,
    )

    command = " ".join(
        segment.text.strip()
        for segment in segments
    ).lower().strip()

    os.remove(filename)

    return command


def execute_command(command):

    print(f"📝 Heard: {command}")

    # Ignore empty/garbage recognition
    if not command:
        print("⚪ Nothing heard.")
        return True

    # Spotify
    if "spotify" in command and (
        "open" in command
        or "launch" in command
        or "start" in command
    ):
        print("🎵 Opening Spotify...")
        subprocess.Popen(["open", "-a", "Spotify"])
        speak("Spotify is open.")
        return True

    # Safari
    if "safari" in command and (
        "open" in command
        or "launch" in command
        or "start" in command
    ):
        print("🌐 Opening Safari...")
        subprocess.Popen(["open", "-a", "Safari"])
        speak("Opening Safari.")
        return True

    # Cursor
    if "cursor" in command and (
        "open" in command
        or "launch" in command
        or "start" in command
    ):
        print("💻 Opening Cursor...")
        subprocess.Popen(["open", "-a", "Cursor"])
        speak("Opening Cursor.")
        return True

    # Time
    if "time" in command:
        current_time = time.strftime("%I:%M %p")
        speak(f"The time is {current_time}.")
        return True

    # Stop
    if (
        "stop" in command
        and ("nexon" in command or "assistant" in command)
    ):
        speak("Goodbye.")
        return False

    # Unknown command
    print("⚠️ Command not available.")
    speak("I don't have that command yet.")
    return True


print("🤖 Nexon is ready.")
speak("Nexon is ready.")

running = True

while running:

    # Short pause prevents Nexon from immediately recording
    # its own spoken response.
    time.sleep(1.5)

    command = record_command()

    running = execute_command(command)

print("🛑 Nexon stopped.")
