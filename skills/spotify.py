import subprocess


def can_handle(command: str) -> bool:
    command = command.lower()

    keywords = [
        "spotify",
        "play music",
        "play a song",
        "pause music",
        "resume music",
    ]

    return any(keyword in command for keyword in keywords)


def handle(command: str) -> str:
    command = command.lower().strip()

    if "open spotify" in command:
        subprocess.Popen(["open", "-a", "Spotify"])
        return "Opening Spotify."

    if "spotify" in command:
        subprocess.Popen(["open", "-a", "Spotify"])
        return "Opening Spotify."

    return "Spotify command received."
