import os
import time
import wave
import tempfile
import subprocess
import logging
import threading

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from google import genai

# Nexus skill router
from skill_router import handle as handle_skill


# ============================================================
#                         NEXUS
#                  Personal AI Assistant
# ============================================================

VERSION = "3.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("NEXUS")


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env from the Nexus project directory
load_dotenv(os.path.join(BASE_DIR, ".env"))

GEMINI_MODEL = "gemini-3.6-flash"

SAMPLE_RATE = 16000
CHANNELS = 1

# Seconds recorded per voice turn
RECORD_SECONDS = 6

# Whisper model
WHISPER_MODEL = "base.en"


# ============================================================
# API CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from your .env file."
    )


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


SYSTEM_PROMPT = """
You are Nexus, a personal AI assistant running on a MacBook.

Personality:
- Intelligent
- Helpful
- Calm
- Friendly
- Slightly futuristic
- Natural and conversational

Rules:
- Answer questions accurately.
- Help with programming and technical topics.
- Keep spoken answers reasonably concise.
- Do not claim to have performed a computer action unless the
  local Nexus skill system actually performed it.
- Do not invent access to files, apps, devices, accounts, or
  information you do not actually have.
- Do not provide dangerous instructions.
"""


def ask_gemini(prompt: str) -> str:
    """
    Send a question to Gemini.
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            SYSTEM_PROMPT
            + "\n\nUser:\n"
            + prompt
        )
    )

    text = getattr(response, "text", None)

    if not text:
        return "I couldn't generate a response."

    return text.strip()


# ============================================================
# WHISPER
# ============================================================

print("🧠 Loading Whisper...")

whisper = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)

print("✅ Whisper ready.")


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(text: str):
    """
    Use macOS built-in speech.
    """

    if not text:
        return

    print(f"\n🔊 Nexus: {text}\n")

    try:
        subprocess.run(
            [
                "/usr/bin/say",
                "-v",
                "Samantha",
                text
            ],
            check=False
        )

    except Exception as exc:
        log.error(
            "TTS error: %s",
            exc
        )


# ============================================================
# MICROPHONE RECORDING
# ============================================================

def record_audio() -> np.ndarray:
    """
    Record one voice turn.
    """

    print("\n🎤 Listening...")

    try:

        audio = sd.rec(
            int(
                RECORD_SECONDS
                * SAMPLE_RATE
            ),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16"
        )

        sd.wait()

        return audio.flatten()

    except Exception as exc:

        log.error(
            "Microphone error: %s",
            exc
        )

        return np.array(
            [],
            dtype=np.int16
        )


# ============================================================
# TEMPORARY WAV FILE
# ============================================================

def save_wav(
    audio: np.ndarray
) -> str:

    fd, filename = tempfile.mkstemp(
        suffix=".wav",
        prefix="nexus_"
    )

    os.close(fd)

    with wave.open(
        filename,
        "wb"
    ) as wav:

        wav.setnchannels(
            CHANNELS
        )

        wav.setsampwidth(2)

        wav.setframerate(
            SAMPLE_RATE
        )

        wav.writeframes(
            audio.tobytes()
        )

    return filename


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe(
    audio: np.ndarray
) -> str:

    if audio.size == 0:
        return ""

    # Simple silence check
    volume = np.abs(
        audio.astype(np.float32)
    ).mean()

    if volume < 100:

        print(
            "🔇 No speech detected."
        )

        return ""

    filename = save_wav(audio)

    print(
        "🧠 Whisper processing..."
    )

    try:

        segments, _ = whisper.transcribe(
            filename,
            language="en",
            vad_filter=True
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return text

    except Exception as exc:

        log.error(
            "Whisper error: %s",
            exc
        )

        return ""

    finally:

        try:
            os.remove(filename)

        except OSError:
            pass


# ============================================================
# SLEEP COMMAND
# ============================================================

def is_sleep_command(
    command: str
) -> bool:

    text = command.lower().strip()

    sleep_phrases = [
        "nexus sleep",
        "nexus stop",
        "stop nexus",
        "go to sleep",
        "stop listening",
        "goodbye nexus",
        "bye nexus",
    ]

    return any(
        phrase in text
        for phrase in sleep_phrases
    )


# ============================================================
# CONTINUOUS VOICE SESSION
# ============================================================

def run_voice_session() -> bool:
    """
    Start a continuous Nexus conversation.

    Flow:

        Microphone
             ↓
          Whisper
             ↓
       Skill Router
         ↙       ↘
      Skill      Gemini
         ↓         ↓
         └────┬────┘
              ↓
             TTS
              ↓
        Listen again
    """

    print()
    print("=" * 55)
    print("             ⚡ NEXUS ACTIVATED")
    print("=" * 55)

    speak(
        "I'm listening."
    )

    while True:

        # ----------------------------------------------------
        # LISTEN
        # ----------------------------------------------------

        audio = record_audio()

        # ----------------------------------------------------
        # TRANSCRIBE
        # ----------------------------------------------------

        command = transcribe(
            audio
        )

        if not command:
            continue

        print(
            f"\n📝 You: {command}"
        )

        # ----------------------------------------------------
        # SLEEP
        # ----------------------------------------------------

        if is_sleep_command(
            command
        ):

            speak(
                "Going to sleep."
            )

            print(
                "💤 Nexus sleeping."
            )

            return True

        # ----------------------------------------------------
        # SKILL ROUTER
        # ----------------------------------------------------

        print(
            "🧩 Checking skills..."
        )

        try:

            skill_response = handle_skill(
                command
            )

        except Exception as exc:

            print(
                f"❌ Skill router error: {exc}"
            )

            skill_response = None

        # ----------------------------------------------------
        # SKILL HANDLED IT
        # ----------------------------------------------------

        if skill_response:

            print(
                f"⚙️ Skill: "
                f"{skill_response}"
            )

            speak(
                skill_response
            )

            print(
                "\n🎤 Ready for your next command..."
            )

            continue

        # ----------------------------------------------------
        # GEMINI FALLBACK
        # ----------------------------------------------------

        print(
            "🧠 No matching skill."
        )

        print(
            "🧠 Sending to Gemini..."
        )

        try:

            answer = ask_gemini(
                command
            )

            speak(
                answer
            )

        except Exception as exc:

            log.error(
                "Gemini error: %s",
                exc
            )

            speak(
                "I'm having trouble "
                "reaching my AI brain."
            )

        # ----------------------------------------------------
        # CONTINUE
        # ----------------------------------------------------

        print(
            "\n🎤 Ready for your next command..."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("                    🤖 NEXUS")
    print("=" * 60)
    print(
        f"                    Version {VERSION}"
    )
    print()
    print(
        "🧠 Gemini: ONLINE"
    )
    print(
        "🎤 Whisper: ONLINE"
    )
    print(
        "🔊 Voice: ONLINE"
    )
    print(
        "🧩 Skills: ONLINE"
    )
    print()
    print(
        "⌘ + Shift + N → Activate through controller"
    )
    print(
        "'Nexus sleep' → End voice session"
    )
    print()
    print("=" * 60)

    try:

        while True:

            choice = input(
                "\nPress ENTER to activate Nexus "
                "or type q to quit: "
            ).strip().lower()

            if choice == "q":

                print(
                    "👋 Nexus shutting down."
                )

                break

            run_voice_session()

    except KeyboardInterrupt:

        print(
            "\n🛑 Nexus stopped."
        )

    except sd.PortAudioError as exc:

        print(
            f"\n❌ Microphone error: {exc}"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
