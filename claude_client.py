"""Safe Claude API helper for Nexon.

The API key is read only from the local ANTHROPIC_API_KEY environment variable.
Never put a real API key in this file or in nexon.py.
"""

import os

try:
    import anthropic
except ImportError:
    anthropic = None

def ask_claude(prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
    if anthropic is None:
        raise RuntimeError("Anthropic SDK is not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Put your new key in the local .env file."
        )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
