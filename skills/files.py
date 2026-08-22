import subprocess
from pathlib import Path


def can_handle(command: str) -> bool:
    command = command.lower()

    keywords = [
        "open downloads",
        "open documents",
        "open desktop",
        "open pictures",
        "open files",
        "show downloads",
        "show desktop",
        "show documents",
    ]

    return any(keyword in command for keyword in keywords)


def handle(command: str) -> str:
    command = command.lower().strip()

    folders = {
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "desktop": Path.home() / "Desktop",
        "pictures": Path.home() / "Pictures",
    }

    for name, path in folders.items():
        if name in command:
            if path.exists():
                subprocess.Popen(["open", str(path)])
                return f"Opening your {name} folder."

            return f"I couldn't find your {name} folder."

    if "open files" in command:
        subprocess.Popen(["open", str(Path.home())])
        return "Opening your home folder."

    return "File command received."
