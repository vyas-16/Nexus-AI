import subprocess
import urllib.parse


def can_handle(command: str) -> bool:
    command = command.lower()

    keywords = [
        "open youtube",
        "open google",
        "search google",
        "search youtube",
        "open github",
    ]

    return any(keyword in command for keyword in keywords)


def handle(command: str) -> str:
    command = command.lower().strip()

    if "search google for " in command:
        query = command.split("search google for ", 1)[1]
        url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote_plus(query)
        )

        subprocess.Popen(["open", url])
        return f"Searching Google for {query}."

    if "search youtube for " in command:
        query = command.split("search youtube for ", 1)[1]
        url = (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote_plus(query)
        )

        subprocess.Popen(["open", url])
        return f"Searching YouTube for {query}."

    if "youtube" in command:
        subprocess.Popen(["open", "https://youtube.com"])
        return "Opening YouTube."

    if "google" in command:
        subprocess.Popen(["open", "https://google.com"])
        return "Opening Google."

    if "github" in command:
        subprocess.Popen(["open", "https://github.com"])
        return "Opening GitHub."

    return "Browser command received."
