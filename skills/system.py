import subprocess
import datetime


# ============================================================
# NEXUS SYSTEM SKILL
# ============================================================

def handle(command: str) -> str:
    command = command.lower().strip()

    # --------------------------------------------------------
    # OPEN MAC APPS
    # --------------------------------------------------------

    apps = {
        "safari": "Safari",
        "chrome": "Google Chrome",
        "finder": "Finder",
        "terminal": "Terminal",
        "notes": "Notes",
        "calculator": "Calculator",
        "calendar": "Calendar",
        "messages": "Messages",
        "mail": "Mail",
        "photos": "Photos",
        "settings": "System Settings",
        "system settings": "System Settings",
    }

    for keyword, app in apps.items():
        if f"open {keyword}" in command or command == keyword:
            subprocess.Popen(["open", "-a", app])
            return f"Opening {app}."

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if "what time" in command or "current time" in command:
        now = datetime.datetime.now()
        return f"It is {now.strftime('%I:%M %p')}."

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        "what date" in command
        or "today's date" in command
        or "todays date" in command
        or command == "date"
    ):
        today = datetime.datetime.now()
        return f"Today is {today.strftime('%A, %B %d, %Y')}."

    # --------------------------------------------------------
    # BATTERY
    # --------------------------------------------------------

    if "battery" in command:

        try:
            result = subprocess.run(
                ["pmset", "-g", "batt"],
                capture_output=True,
                text=True
            )

            output = result.stdout

            for part in output.split(";"):
                if "%" in part:
                    battery = part.strip()
                    return f"Your battery is {battery}."

            return "I couldn't read your battery level."

        except Exception:
            return "I couldn't access the battery information."

    # --------------------------------------------------------
    # STORAGE
    # --------------------------------------------------------

    if (
        "storage" in command
        or "disk space" in command
        or "free space" in command
    ):

        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True
            )

            lines = result.stdout.strip().splitlines()

            if len(lines) >= 2:
                parts = lines[-1].split()

                if len(parts) >= 4:
                    total = parts[1]
                    used = parts[2]
                    available = parts[3]

                    return (
                        f"You have {available} available "
                        f"out of {total} storage."
                    )

            return "I couldn't read your storage information."

        except Exception:
            return "I couldn't access your storage information."

    # --------------------------------------------------------
    # CPU / PROCESSOR
    # --------------------------------------------------------

    if "processor" in command or "cpu" in command:

        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True
            )

            cpu = result.stdout.strip()

            if cpu:
                return f"Your processor is {cpu}."

        except Exception:
            pass

        return "I couldn't read your processor information."

    # --------------------------------------------------------
    # RAM
    # --------------------------------------------------------

    if "ram" in command or "memory" in command:

        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True
            )

            bytes_ram = int(result.stdout.strip())
            gb = bytes_ram / (1024 ** 3)

            return f"Your Mac has approximately {gb:.0f} gigabytes of RAM."

        except Exception:
            return "I couldn't read your memory information."

    # --------------------------------------------------------
    # MAC / SYSTEM INFORMATION
    # --------------------------------------------------------

    if (
        "system information" in command
        or "mac information" in command
        or "computer information" in command
    ):

        try:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True
            )

            output = result.stdout

            model = "Unknown"
            chip = "Unknown"
            memory = "Unknown"

            for line in output.splitlines():

                line = line.strip()

                if line.startswith("Model Name:"):
                    model = line.split(":", 1)[1].strip()

                elif line.startswith("Chip:"):
                    chip = line.split(":", 1)[1].strip()

                elif line.startswith("Memory:"):
                    memory = line.split(":", 1)[1].strip()

            return (
                f"Your Mac is a {model}, "
                f"with {chip} and {memory} of memory."
            )

        except Exception:
            return "I couldn't read your Mac information."

    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if (
        "take a screenshot" in command
        or "take screenshot" in command
        or "screenshot" in command
    ):

        try:
            subprocess.Popen(
                ["screencapture", "-i", "screenshot.png"]
            )

            return "Screenshot tool opened."

        except Exception:
            return "I couldn't start the screenshot tool."

    # --------------------------------------------------------
    # LOCK MAC
    # --------------------------------------------------------

    if (
        "lock my mac" in command
        or "lock the mac" in command
    ):

        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "q" using {control down, command down}'
                ]
            )

            return "Locking your Mac."

        except Exception:
            return "I couldn't lock the Mac."

    # --------------------------------------------------------
    # UNKNOWN SYSTEM COMMAND
    # --------------------------------------------------------

    return "System command received."
