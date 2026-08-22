#!/usr/bin/env python3
"""Safer Nexon-style double-clap desktop assistant.

Safety-oriented defaults:
- Does NOT open trading/financial sites.
- Does NOT use your normal Chrome profile. Optional web actions use isolated profiles.
- Does NOT execute shell commands or PowerShell.
- ElevenLabs TTS is opt-in and only contacted when explicitly enabled.
- Cursor action only focuses/launches Cursor; no arbitrary commands are passed to it.
- All URLs are explicit allowlisted constants/environment values and are opened as URLs.
- No bundled __pycache__, binaries, or hidden payloads.
"""
from __future__ import annotations

import hashlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
import numpy as np
import sounddevice as sd

# ----------------------------- safe defaults -----------------------------
SAMPLE_RATE = 44100
BLOCK_MS = 40
CHANNELS = 1
SPIKE_RATIO = 7.0
COOLDOWN_S = 0.45
MIN_DOUBLE_GAP_S = 0.05
MAX_DOUBLE_GAP_S = 0.35
RETRIGGER_RATIO = 0.55
NOISE_FLOOR_ALPHA = 0.992
MIN_RMS = 0.012
QUIET_GATE_MULT = 2.2
INPUT_PROBE_S = 0.5
INPUT_SILENT_RMS = 0.001

# Safe actions: Spotify + Cursor are enabled. Financial/trading sites are removed.
SONG_URI = "https://open.spotify.com/track/39shmbIHICJ2Wxnk1fPSdz"
OPEN_CLAUDE_IN_CHROME = False
CLAUDE_URL = "https://claude.ai/new"
OPEN_SPOTIFY = True
OPEN_CURSOR = True
CURSOR_FULLSCREEN = False

# Web actions always use an isolated temporary Chrome profile by default.
USE_ISOLATED_CHROME_PROFILE = True
OPEN_CHROME_FULLSCREEN = False
CHROME_WINDOW_WIDTH = 1400
CHROME_WINDOW_HEIGHT = 900
CHROME_NEW_WINDOW_WAIT_S = 15.0

# TTS is opt-in. Set JARVIS_TTS_ENABLED=true and provide ElevenLabs credentials.
JARVIS_TTS_ENABLED = False
JARVIS_WELCOME_PHRASE = "Welcome back. Nexon is ready."
JARVIS_WELCOME_CACHE_ENABLED = True

load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger("jarvis_safe")


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def safe_url(raw: str, allowed_hosts: set[str]) -> str | None:
    """Accept only HTTPS URLs for explicitly allowed hosts."""
    value = raw.strip()
    try:
        p = urlparse(value)
    except ValueError:
        return None
    if p.scheme != "https" or not p.hostname or p.hostname.lower() not in allowed_hosts:
        log.warning("Blocked non-allowlisted URL: %s", value)
        return None
    return value


def block_samples() -> int:
    return max(int(SAMPLE_RATE * BLOCK_MS / 1000), 1)


def rms_mono(block: np.ndarray) -> float:
    if block.ndim > 1:
        block = np.mean(block.astype(np.float64), axis=1)
    else:
        block = block.astype(np.float64)
    return float(np.sqrt(np.mean(block ** 2))) if block.size else 0.0


def input_devices() -> list[tuple[int, dict]]:
    return [(i, d) for i, d in enumerate(sd.query_devices()) if d["max_input_channels"] >= 1]


def resolve_input_device(spec: str) -> int:
    spec = spec.strip()
    if spec.isdigit():
        idx = int(spec)
        sd.query_devices(idx)
        return idx
    needle = spec.lower()
    for idx, dev in input_devices():
        if needle in dev["name"].lower():
            return idx
    raise ValueError(f"No input device matches {spec!r}")


def probe_input(device: int, blocksize: int) -> float | None:
    try:
        with sd.InputStream(device=device, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", blocksize=blocksize) as stream:
            peak = 0.0
            deadline = time.monotonic() + INPUT_PROBE_S
            while time.monotonic() < deadline:
                data, _ = stream.read(blocksize)
                peak = max(peak, rms_mono(data))
            return peak
    except sd.PortAudioError:
        return None


def choose_input_device(blocksize: int) -> int:
    override = (os.environ.get("JARVIS_INPUT_DEVICE") or "").strip()
    if override:
        try:
            return resolve_input_device(override)
        except ValueError as exc:
            log.error("%s", exc)
            raise SystemExit(1) from exc

    default = sd.default.device[0]
    if default is not None and default >= 0:
        peak = probe_input(default, blocksize)
        if peak is not None and peak >= INPUT_SILENT_RMS:
            return default

    best_idx, best_peak = None, -1.0
    for idx, _ in input_devices():
        if default is not None and idx == default:
            continue
        peak = probe_input(idx, blocksize)
        if peak is not None and peak > best_peak:
            best_idx, best_peak = idx, peak
    if best_idx is not None and best_peak >= INPUT_SILENT_RMS:
        return best_idx
    if default is not None and default >= 0:
        return default
    devices = input_devices()
    if not devices:
        raise SystemExit("No microphone/input devices found.")
    return devices[0][0]


def chrome_executable() -> str | None:
    if sys.platform == "win32":
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), os.environ.get("LOCALAPPDATA", "")):
            if base:
                candidate = os.path.join(base, "Google", "Chrome", "Application", "chrome.exe")
                if os.path.isfile(candidate):
                    return candidate
    return shutil.which("google-chrome") or shutil.which("chrome")


def isolated_profile(site: str) -> str:
    root = Path(tempfile.gettempdir()) / "Nexon-safe-chrome" / site
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def open_url(url: str, label: str, allowed_hosts: set[str], isolated_site: str | None = None) -> None:
    u = safe_url(url, allowed_hosts)
    if not u:
        return
    chrome = chrome_executable()
    try:
        if chrome:
            args = [chrome, "--new-window"]
            if USE_ISOLATED_CHROME_PROFILE and isolated_site:
                args += [f"--user-data-dir={isolated_profile(isolated_site)}", "--no-first-run", "--no-default-browser-check"]
            if not OPEN_CHROME_FULLSCREEN:
                args.append(f"--window-size={CHROME_WINDOW_WIDTH},{CHROME_WINDOW_HEIGHT}")
            args.append(u)
            kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            subprocess.Popen(args, **kwargs)
        else:
            webbrowser.open(u)
        log.info("Opened %s", label)
    except OSError as exc:
        log.warning("Could not open %s: %s", label, exc)


def play_song() -> None:
    if not OPEN_SPOTIFY:
        return
    url = safe_url(SONG_URI, {"open.spotify.com"})
    if not url:
        return
    try:
        if sys.platform == "win32":
            os.startfile(url)
        else:
            webbrowser.open(url)
    except OSError as exc:
        log.warning("Could not open Spotify: %s", exc)


def cursor_executable() -> str | None:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA", "")
        for rel in (r"Programs\cursor\Cursor.exe", r"Programs\Cursor\Cursor.exe"):
            if local:
                candidate = os.path.join(local, *rel.split("\\"))
                if os.path.isfile(candidate):
                    return candidate
    return shutil.which("cursor")


def focus_cursor_windows() -> bool:
    if sys.platform != "win32":
        return False
    # Deliberately use only the Windows API to find Cursor windows; no shell commands.
    import ctypes
    from ctypes import wintypes
    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    found: list[tuple[int, int]] = []
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    GW_OWNER, GWL_EXSTYLE, WS_EX_TOOLWINDOW = 4, -20, 0x80

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum(hwnd, _):
        if user32.GetWindow(hwnd, GW_OWNER) or user32.GetWindowLongW(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW:
            return True
        if not user32.IsWindowVisible(hwnd) and not user32.IsIconic(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return True
        hproc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if not hproc:
            return True
        try:
            buf = ctypes.create_unicode_buffer(4096)
            size = wintypes.DWORD(len(buf))
            if not kernel32.QueryFullProcessImageNameW(hproc, 0, buf, ctypes.byref(size)):
                return True
            if os.path.basename(buf.value).lower() != "cursor.exe":
                return True
        finally:
            kernel32.CloseHandle(hproc)
        r = wintypes.RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(r)):
            area = max(0, r.right-r.left) * max(0, r.bottom-r.top)
            if area > 40000:
                found.append((area, int(hwnd)))
        return True

    user32.EnumWindows(enum, 0)
    if not found:
        return False
    hwnd = max(found)[1]
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    return True


def open_cursor() -> None:
    if not OPEN_CURSOR:
        return
    exe = cursor_executable()
    if not exe:
        log.info("Cursor not found; skipping.")
        return
    if sys.platform == "win32" and focus_cursor_windows():
        log.info("Focused existing Cursor window.")
        return
    kwargs = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        subprocess.Popen([exe], **kwargs)
        log.info("Launched Cursor.")
    except OSError as exc:
        log.warning("Could not launch Cursor: %s", exc)


def tts_welcome() -> None:
    if not env_bool("JARVIS_TTS_ENABLED", JARVIS_TTS_ENABLED):
        return
    voice = (os.environ.get("ELEVENLABS_VOICE_ID") or "").strip()
    key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not voice or not key:
        log.warning("TTS enabled but ElevenLabs credentials are missing; skipping TTS.")
        return
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        log.warning("ElevenLabs package not installed; skipping TTS.")
        return
    text = JARVIS_WELCOME_PHRASE.strip()
    model = (os.environ.get("ELEVENLABS_MODEL_ID") or "eleven_multilingual_v2").strip()
    fmt = (os.environ.get("ELEVENLABS_OUTPUT_FORMAT") or "pcm_24000").strip()
    rate = 24000
    try:
        if fmt.startswith("pcm_"):
            rate = int(fmt.split("_", 1)[1])
    except ValueError:
        pass
    cache_dir = Path(__file__).resolve().parent / ".cache" / "jarvis_welcome"
    digest = hashlib.sha256(f"{text}|{voice}|{model}|{fmt}".encode()).hexdigest()[:24]
    cache = cache_dir / f"{digest}.wav"

    raw: bytes | None = None
    if JARVIS_WELCOME_CACHE_ENABLED and cache.is_file():
        try:
            with wave.open(str(cache), "rb") as wf:
                raw = wf.readframes(wf.getnframes())
                rate = wf.getframerate()
        except (OSError, wave.Error):
            raw = None
    if raw is None:
        try:
            client = ElevenLabs(api_key=key)
            raw = b"".join(client.text_to_speech.convert(voice_id=voice, text=text, model_id=model, output_format=fmt))
        except Exception as exc:
            log.warning("ElevenLabs TTS failed: %s", exc)
            return
        if JARVIS_WELCOME_CACHE_ENABLED and raw:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                with wave.open(str(cache), "wb") as wf:
                    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate); wf.writeframes(raw)
            except OSError as exc:
                log.warning("Could not cache TTS audio: %s", exc)
    if raw:
        try:
            sd.play(np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0, rate)
            sd.wait()
        except Exception as exc:
            log.warning("Could not play TTS audio: %s", exc)


def run_actions_once() -> None:
    play_song()
    if sys.platform == "darwin":
        subprocess.Popen(["/usr/bin/say","Welcome Back.Nexon is Ready."])
    if OPEN_CLAUDE_IN_CHROME:
        open_url(CLAUDE_URL, "Claude", {"claude.ai"}, "claude")
    open_cursor()
    threading.Thread(target=tts_welcome, daemon=True).start()


def main() -> int:
    blocksize = block_samples()
    noise_floor = 1e-4
    last_trigger = 0.0
    first_clap: float | None = None
    armed = True
    triggered_once = False

    log.info("Nexon Safe is listening for a double clap. Press Ctrl+C to stop.")
    log.info("Safe defaults: no trading sites, isolated Chrome profile, TTS off, no shell commands.")
    input_idx = choose_input_device(blocksize)

    try:
        with sd.InputStream(device=input_idx, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", blocksize=blocksize) as stream:
            while True:
                data, overflowed = stream.read(blocksize)
                if overflowed:
                    log.warning("Audio input overflow; consider increasing BLOCK_MS.")
                level = rms_mono(data)
                if level < noise_floor * QUIET_GATE_MULT:
                    noise_floor = max(NOISE_FLOOR_ALPHA * noise_floor + (1-NOISE_FLOOR_ALPHA) * level, 1e-7)
                threshold = max(noise_floor * SPIKE_RATIO, MIN_RMS)
                now = time.monotonic()
                if level < threshold * RETRIGGER_RATIO:
                    armed = True
                if armed and level >= threshold and now - last_trigger >= COOLDOWN_S:
                    armed = False
                    if first_clap is None:
                        first_clap = now
                    else:
                        gap = now - first_clap
                        if MIN_DOUBLE_GAP_S <= gap <= MAX_DOUBLE_GAP_S:
                            first_clap = None
                            last_trigger = now
                            log.info("Double clap detected (gap=%.3fs).", gap)
                            if not triggered_once:
                                triggered_once = True
                                threading.Thread(target=run_actions_once, daemon=True).start()
                        elif gap > MAX_DOUBLE_GAP_S:
                            first_clap = now
    except KeyboardInterrupt:
        log.info("Stopped.")
        return 0
    except sd.PortAudioError as exc:
        log.error("Audio error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
