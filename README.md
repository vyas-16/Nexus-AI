# Nexon Safe

A safety-first version of the clap-triggered desktop assistant.

## What changed from the original

- Removed the Binance/trading action entirely.
- Claude is **off by default**.
- Chrome web actions use a separate temporary profile instead of your normal Chrome cookies/extensions.
- Only HTTPS URLs on an explicit allowlist are opened.
- ElevenLabs TTS is **off by default** and only contacts ElevenLabs when you explicitly enable it.
- No shell/PowerShell commands, `eval`, `exec`, downloads, or arbitrary command strings.
- Cursor is only focused/launched; no command is passed to it.
- The project contains source/config/docs only — no compiled `.pyc` or executable payload.

## Install

Use a fresh virtual environment if possible:

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python Nexon.py
```

## Optional TTS

Copy `.env.example` to `.env`, add your own ElevenLabs credentials, then set:

```env
JARVIS_TTS_ENABLED=true
```

Never commit `.env` or your API key.

## Safety notes

The microphone is intentionally accessed while the program is running because clap detection requires it. Stop the program with `Ctrl+C` when you do not want it listening.

Chrome automation uses a temporary profile under the OS temp directory. This means existing Chrome logins/cookies are not reused.
