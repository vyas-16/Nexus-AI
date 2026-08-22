import json
import urllib.request


# ============================================================
# NEXUS LOCAL AI COMMAND PLANNER
# ============================================================

MODEL = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def understand(command: str):

    prompt = f"""
You are Nexus, a fast macOS computer-control command planner.

Understand the user's natural language and convert it into
ONE simple command.

Return ONLY the command.
No explanation.
No markdown.
No extra words.

AVAILABLE COMMANDS:

open safari
open calculator
open spotify
open finder
open terminal
open notes
open calendar
open chrome
open vscode

new tab
close tab
refresh
go back
go forward
scroll up
scroll down

press enter
press escape
press tab
press space

copy
paste
select all

type <text>

open safari and search youtube for <query>
open safari and search google for <query>

play
pause
forward <number> seconds
back <number> seconds
fullscreen


EXAMPLES:

User:
"Can you open Safari?"

Command:
open safari


User:
"Launch the calculator."

Command:
open calculator


User:
"I want to watch Baby Shark."

Command:
open safari and search youtube for Baby Shark


User:
"Get me Ronaldo highlights on YouTube."

Command:
open safari and search youtube for Ronaldo highlights


User:
"Pause the video."

Command:
pause


User:
"Stop playing."

Command:
pause


User:
"Continue."

Command:
play


User:
"Resume the video."

Command:
play


User:
"Skip ahead 30 seconds."

Command:
forward 30 seconds


User:
"Move forward by half a minute."

Command:
forward 30 seconds


User:
"Go forward 45 seconds."

Command:
forward 45 seconds


User:
"Go back 10 seconds."

Command:
back 10 seconds


User:
"Rewind 20 seconds."

Command:
back 20 seconds


User:
"Make the video fullscreen."

Command:
fullscreen


User:
"Give me a new browser tab."

Command:
new tab


User:
"Scroll down."

Command:
scroll down


User:
"Press the enter key."

Command:
press enter


User:
"Type hello world."

Command:
type hello world


SPECIAL CASE:

If the user says something like:

"Start the video from 1 minute 20 seconds"

or:

"Play it from 1:20"

convert the requested time into seconds and return:

forward 80 seconds

Examples:

"start from 30 seconds"
-> forward 30 seconds

"start from 1 minute"
-> forward 60 seconds

"start from 1 minute 20 seconds"
-> forward 80 seconds

"start from 2 minutes 10 seconds"
-> forward 130 seconds

"start from 1:30"
-> forward 90 seconds


If the request is NOT a computer action, return exactly:

NOT_COMPUTER


USER REQUEST:
{command}
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    try:

        data = json.dumps(
            payload
        ).encode("utf-8")

        request = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = result.get(
            "response",
            ""
        ).strip()

        answer = (
            answer
            .replace("```", "")
            .strip()
            .strip('"')
            .strip("'")
        )

        if not answer:
            return None

        if answer.upper() == "NOT_COMPUTER":
            return None

        return answer

    except Exception as exc:

        print(
            f"⚠️ Local AI unavailable: {exc}"
        )

        return None
