from google import genai

client = genai.Client()

MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """
You are Nexus, a friendly personal AI assistant.
Answer questions clearly and naturally.
Do not claim to have performed computer actions.
Keep answers reasonably concise because they will be spoken aloud.
"""

def ask_nexus(text: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"{SYSTEM_PROMPT}\n\nUser: {text}"
    )
    return response.text.strip()


if __name__ == "__main__":
    question = input("You: ")
    print("Nexus:", ask_nexus(question))
