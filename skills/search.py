import os
from google import genai
from google.genai import types


# ============================================================
# NEXUS WEB SEARCH SKILL
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def can_handle(command: str) -> bool:
    command = command.lower()

    keywords = [
        "search for",
        "search the web",
        "search web",
        "look up",
        "google",
        "find information",
        "latest",
        "news",
        "what happened",
        "current",
        "today",
        "weather",
    ]

    return any(
        keyword in command
        for keyword in keywords
    )


def handle(command: str) -> str:

    command = command.strip()

    if not command:
        return "What would you like me to search for?"

    try:

        print("🌐 Nexus is searching the web...")

        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=command,
            config=config
        )

        if response.text:
            return response.text.strip()

        return "I couldn't find a useful answer."

    except Exception as exc:

        print(f"❌ Web search error: {exc}")

        return (
            "I couldn't reach the web search service "
            "right now."
        )
