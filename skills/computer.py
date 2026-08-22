import subprocess
import re
import time
import urllib.parse


APP_ALIASES = {
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "calculator": "Calculator",
    "finder": "Finder",
    "terminal": "Terminal",
    "spotify": "Spotify",
    "notes": "Notes",
    "calendar": "Calendar",
    "messages": "Messages",
    "mail": "Mail",
    "photos": "Photos",
    "music": "Music",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
}


# ============================================================
# BASIC
# ============================================================

def clean_command(command: str):

    command = command.lower().strip()

    command = re.sub(
        r"^(hey\s+)?nexus[\s,:-]*",
        "",
        command
    )

    return command.strip()


def run_applescript(script: str):

    try:

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode != 0:

            print(
                "AppleScript error:",
                result.stderr.strip()
            )

            return "I couldn't control the Mac."

        return result.stdout.strip()

    except Exception as exc:

        print(
            "Computer control error:",
            exc
        )

        return "I couldn't control the Mac."


# ============================================================
# APPS
# ============================================================

def open_app(app: str):

    try:

        subprocess.Popen(
            ["open", "-a", app]
        )

        time.sleep(1)

        return f"Opened {app}."

    except Exception as exc:

        print(exc)

        return f"I couldn't open {app}."


def activate_app(app: str):

    script = f'''
    tell application "{app}"
        activate
    end tell
    '''

    result = run_applescript(script)

    if result.startswith("I couldn't"):
        return result

    return f"{app} is active."


# ============================================================
# KEYBOARD
# ============================================================

KEY_CODES = {
    "enter": 36,
    "return": 36,
    "escape": 53,
    "esc": 53,
    "tab": 48,
    "space": 49,
    "delete": 51,
    "backspace": 51,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
}


def press_key(key: str):

    key = key.lower().strip()

    if key not in KEY_CODES:

        return f"I don't know the key {key}."

    script = f'''
    tell application "System Events"
        key code {KEY_CODES[key]}
    end tell
    '''

    return run_applescript(script) or "Done."


def hotkey(keys):

    modifiers = {
        "command": "command down",
        "cmd": "command down",
        "control": "control down",
        "ctrl": "control down",
        "option": "option down",
        "alt": "option down",
        "shift": "shift down",
    }

    modifier_list = []
    normal_key = None

    for key in keys:

        key = key.lower().strip()

        if key in modifiers:

            modifier_list.append(
                modifiers[key]
            )

        else:

            normal_key = key

    if not normal_key:

        return "I couldn't understand that shortcut."

    modifier_text = ", ".join(
        modifier_list
    )

    script = f'''
    tell application "System Events"
        keystroke "{normal_key}" using {{{modifier_text}}}
    end tell
    '''

    return run_applescript(script) or "Done."


def type_text(text: str):

    escaped = (
        text
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )

    script = f'''
    tell application "System Events"
        keystroke "{escaped}"
    end tell
    '''

    return run_applescript(script) or "Done."


# ============================================================
# SAFARI JAVASCRIPT
# ============================================================

def safari_javascript(script: str):

    escaped = (
        script
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
    )

    applescript = f'''
    tell application "Safari"
        tell front window
            tell current tab
                do JavaScript "{escaped}"
            end tell
        end tell
    end tell
    '''

    return run_applescript(
        applescript
    )


# ============================================================
# SAFARI NAVIGATION
# ============================================================

def safari_address(url: str):

    open_app("Safari")

    time.sleep(1)

    hotkey(["command", "l"])

    time.sleep(0.2)

    type_text(url)

    press_key("enter")

    return "Done."


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query: str):

    query = query.strip()

    if not query:

        return "I need something to search for."

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote_plus(query)
    )

    safari_address(url)

    time.sleep(3)

    return (
        f"Searching YouTube for {query}."
    )


# ============================================================
# OPEN FIRST YOUTUBE RESULT
# ============================================================

def youtube_open_first_result():

    activate_app("Safari")

    time.sleep(1)

    script = """
    (function() {

        const links =
            Array.from(
                document.querySelectorAll('a')
            );

        const video =
            links.find(
                a =>
                    a.href &&
                    a.href.includes('/watch?v=')
            );

        if (!video) {

            return 'NO_VIDEO';

        }

        video.click();

        return 'OPENED';

    })();
    """

    result = safari_javascript(
        script
    )

    if "NO_VIDEO" in result:

        return (
            "I couldn't find a YouTube video."
        )

    if "OPENED" in result:

        time.sleep(3)

        return (
            "Opened the first YouTube video."
        )

    return (
        "I couldn't open the YouTube result."
    )


# ============================================================
# YOUTUBE PLAY / PAUSE
# ============================================================

def youtube_play():

    activate_app("Safari")

    time.sleep(0.3)

    press_key("space")

    return "Playing."


def youtube_pause():

    activate_app("Safari")

    time.sleep(0.3)

    press_key("space")

    return "Paused."


# ============================================================
# YOUTUBE SEEK
# ============================================================

def youtube_forward(seconds):

    activate_app("Safari")

    time.sleep(0.3)

    presses = max(
        1,
        round(seconds / 5)
    )

    for _ in range(presses):

        press_key("right")

        time.sleep(0.04)

    return (
        f"Forwarded {seconds} seconds."
    )


def youtube_backward(seconds):

    activate_app("Safari")

    time.sleep(0.3)

    presses = max(
        1,
        round(seconds / 5)
    )

    for _ in range(presses):

        press_key("left")

        time.sleep(0.04)

    return (
        f"Went back {seconds} seconds."
    )


def youtube_fullscreen():

    activate_app("Safari")

    time.sleep(0.3)

    press_key("f")

    return "Fullscreen toggled."


# ============================================================
# YOUTUBE COMMAND HANDLER
# ============================================================

def handle_youtube_command(command):

    # --------------------------------------------------------
    # SEARCH YOUTUBE
    #
    # Supports:
    # search youtube for X
    # search on youtube for X
    # search youtube X
    # find X on youtube
    # get X on youtube
    # play X on youtube
    # open X in youtube
    # --------------------------------------------------------

    patterns = [

        r"search youtube for (.+)",

        r"search on youtube for (.+)",

        r"search youtube (.+)",

        r"find (.+) on youtube",

        r"get (.+) on youtube",

        r"play (.+) on youtube",

        r"open (.+) on youtube",

        r"open (.+) in youtube",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            command
        )

        if match:

            query = match.group(1).strip()

            youtube_search(query)

            return (
                f"Searching YouTube for {query}."
            )

    # --------------------------------------------------------
    # OPEN FIRST RESULT
    # --------------------------------------------------------

    if command in [

        "open first result",
        "open the first result",
        "click first result",
        "click the first result",
        "play first result",
        "play the first result",
        "open first video",
        "open the first video",

    ]:

        return youtube_open_first_result()

    # --------------------------------------------------------
    # PAUSE
    # --------------------------------------------------------

    if command in [

        "pause",
        "pause it",
        "pause video",
        "pause the video",
        "stop the video",

    ]:

        return youtube_pause()

    # --------------------------------------------------------
    # PLAY
    # --------------------------------------------------------

    if command in [

        "play",
        "play it",
        "resume",
        "resume it",
        "continue",
        "continue playing",

    ]:

        return youtube_play()

    # --------------------------------------------------------
    # FORWARD
    # --------------------------------------------------------

    match = re.search(
        r"(?:skip|forward|go forward)"
        r"\s+(\d+)\s*seconds?",
        command
    )

    if match:

        return youtube_forward(
            int(match.group(1))
        )

    # --------------------------------------------------------
    # BACKWARD
    # --------------------------------------------------------

    match = re.search(
        r"(?:go back|back|rewind)"
        r"\s+(\d+)\s*seconds?",
        command
    )

    if match:

        return youtube_backward(
            int(match.group(1))
        )

    # --------------------------------------------------------
    # FULLSCREEN
    # --------------------------------------------------------

    if (
        "fullscreen" in command
        or "full screen" in command
    ):

        return youtube_fullscreen()

    return None


# ============================================================
# MULTI-STEP COMMANDS
# ============================================================

def handle_multi_step(command):

    # --------------------------------------------------------
    # OPEN SAFARI + SEARCH YOUTUBE
    # --------------------------------------------------------

    match = re.search(
        r"open safari and "
        r"(?:search youtube for|"
        r"search on youtube for|"
        r"search youtube|"
        r"find|"
        r"play|"
        r"watch|get) "
        r"(.+)",
        command
    )

    if match:

        query = match.group(1).strip()

        youtube_search(query)

        return (
            f"Searching YouTube for {query}."
        )

    # --------------------------------------------------------
    # SEARCH + OPEN FIRST RESULT
    # --------------------------------------------------------

    match = re.search(
        r"(?:search|find|get|open|play)"
        r"\s+(.+?)"
        r"\s+(?:on|in)\s+youtube"
        r"\s+and\s+"
        r"(?:open|play)"
        r"\s+(?:the\s+)?first"
        r"(?:\s+result|\s+video)?",
        command
    )

    if match:

        query = match.group(1).strip()

        youtube_search(query)

        time.sleep(3)

        youtube_open_first_result()

        return (
            f"Found {query} and opened "
            "the first video."
        )

    return None


# ============================================================
# COMMAND DETECTION
# ============================================================

def can_handle(command):

    command = clean_command(
        command
    )

    if not command:

        return False

    youtube_words = [

        "youtube",
        "pause",
        "resume",
        "skip",
        "rewind",
        "forward",
        "fullscreen",
        "full screen",
        "first result",
        "first video",

    ]

    if any(
        word in command
        for word in youtube_words
    ):

        return True

    if command.startswith(
        (
            "open ",
            "launch ",
            "start ",
            "go to ",
        )
    ):

        for alias in APP_ALIASES:

            if alias in command:

                return True

    if command.startswith(
        "type "
    ):

        return True

    keyboard_commands = [

        "enter",
        "press enter",
        "press escape",
        "press tab",
        "press space",
        "scroll up",
        "scroll down",
        "new tab",
        "close tab",
        "refresh",
        "reload",
        "go back",
        "go forward",
        "copy",
        "paste",
        "select all",

    ]

    if command in keyboard_commands:

        return True

    return False


# ============================================================
# MAIN
# ============================================================

def handle(command):

    command = clean_command(
        command
    )

    # Multi-step
    result = handle_multi_step(
        command
    )

    if result:

        return result

    # YouTube
    result = handle_youtube_command(
        command
    )

    if result:

        return result

    # Apps
    for alias, app in APP_ALIASES.items():

        if command in [

            f"open {alias}",
            f"launch {alias}",
            f"start {alias}",
            f"go to {alias}",

        ]:

            return open_app(app)

    # Type
    if command.startswith(
        "type "
    ):

        return type_text(
            command[5:].strip()
        )

    # Keys
    for key in KEY_CODES:

        if command in [

            key,
            f"press {key}",

        ]:

            return press_key(key)

    # Shortcuts
    if command in [
        "new tab",
        "open new tab",
    ]:

        return hotkey(
            ["command", "t"]
        )

    if command in [
        "close tab",
        "close this tab",
    ]:

        return hotkey(
            ["command", "w"]
        )

    if command in [
        "refresh",
        "refresh page",
        "reload",
        "reload page",
    ]:

        return hotkey(
            ["command", "r"]
        )

    if command in [
        "go back",
        "back",
    ]:

        return hotkey(
            ["command", "["]
        )

    if command in [
        "go forward",
        "forward",
    ]:

        return hotkey(
            ["command", "]"]
        )

    if command == "copy":

        return hotkey(
            ["command", "c"]
        )

    if command == "paste":

        return hotkey(
            ["command", "v"]
        )

    if command in [
        "select all",
        "select everything",
    ]:

        return hotkey(
            ["command", "a"]
        )

    # Activate
    for prefix in [
        "switch to ",
        "focus ",
        "activate ",
    ]:

        if command.startswith(prefix):

            app_name = command[
                len(prefix):
            ].strip()

            app = APP_ALIASES.get(
                app_name,
                app_name.title()
            )

            return activate_app(app)

    return (
        "I couldn't understand "
        "that computer command."
    )
