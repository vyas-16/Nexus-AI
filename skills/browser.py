import subprocess
import urllib.parse
import re


# ============================================================
# NEXUS BROWSER SKILL
# Natural-language browser, search and YouTube actions
# ============================================================


WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "google maps": "https://maps.google.com",
    "reddit": "https://www.reddit.com",
    "stackoverflow": "https://stackoverflow.com",
    "linkedin": "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "amazon": "https://www.amazon.in",
}


# ============================================================
# COMMAND CLEANING
# ============================================================

def clean_command(command: str) -> str:
    """
    Remove Nexus wake word and normalize the command.
    """

    command = command.lower().strip()

    command = re.sub(
        r"^(hey\s+)?nexus[\s,:-]*",
        "",
        command
    ).strip()

    return command


# ============================================================
# URL OPENING
# ============================================================

def open_url(url: str) -> None:
    """
    Open a URL using the default macOS browser.
    """

    subprocess.Popen(
        ["open", url]
    )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def search_google(query: str) -> str:

    query = query.strip()

    if not query:
        return "What should I search for?"

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )

    open_url(url)

    return f"Searching Google for {query}."


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def search_youtube(query: str) -> str:

    query = query.strip()

    if not query:
        return "What would you like me to find on YouTube?"

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote_plus(query)
    )

    open_url(url)

    return f"Searching YouTube for {query}."


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(command: str) -> str:

    for website, url in WEBSITES.items():

        if website in command:

            open_url(url)

            return f"Opening {website.title()}."

    return "I couldn't identify the website."


# ============================================================
# YOUTUBE INTENT
# ============================================================

def handle_youtube_action(command: str) -> str:
    """
    Understand commands such as:

        play baby shark
        play baby shark on youtube
        watch python tutorial
        find avengers trailer on youtube
        search youtube for python
    """

    # --------------------------------------------------------
    # PLAY
    # --------------------------------------------------------

    play_patterns = [
        "play ",
        "play the song ",
        "play the video ",
    ]

    for pattern in play_patterns:

        if command.startswith(pattern):

            query = command[len(pattern):].strip()

            query = re.sub(
                r"\s+on\s+youtube$",
                "",
                query,
                flags=re.IGNORECASE
            ).strip()

            if query:
                return search_youtube(query)

            return "What would you like me to play?"

    # --------------------------------------------------------
    # WATCH
    # --------------------------------------------------------

    watch_patterns = [
        "watch ",
        "watch the ",
    ]

    for pattern in watch_patterns:

        if command.startswith(pattern):

            query = command[len(pattern):].strip()

            query = re.sub(
                r"\s+on\s+youtube$",
                "",
                query,
                flags=re.IGNORECASE
            ).strip()

            if query:
                return search_youtube(query)

            return "What would you like me to watch?"

    # --------------------------------------------------------
    # FIND ON YOUTUBE
    # --------------------------------------------------------

    patterns = [
        "find on youtube ",
        "search youtube for ",
        "search youtube ",
        "look up on youtube ",
        "find youtube ",
    ]

    for pattern in patterns:

        if pattern in command:

            query = command.split(
                pattern,
                1
            )[1].strip()

            if query:
                return search_youtube(query)

    return None


# ============================================================
# GOOGLE SEARCH INTENT
# ============================================================

def handle_google_search(command: str) -> str:
    """
    Understand natural Google search commands.
    """

    patterns = [
        "search google for ",
        "search google ",
        "google search for ",
        "google search ",
        "search the web for ",
        "search web for ",
        "search the internet for ",
        "look up on google ",
        "find on google ",
    ]

    for pattern in patterns:

        if pattern in command:

            query = command.split(
                pattern,
                1
            )[1].strip()

            if query:
                return search_google(query)

            return "What should I search for?"

    return None


# ============================================================
# GENERIC SEARCH
# ============================================================

def handle_generic_search(command: str) -> str:
    """
    Commands like:

        search Python
        find C programming tutorials
        look up machine learning
    """

    patterns = [
        "search ",
        "find ",
        "look up ",
    ]

    for pattern in patterns:

        if command.startswith(pattern):

            query = command[len(pattern):].strip()

            # Avoid treating website-opening commands as searches
            if query in WEBSITES:
                return None

            if query:
                return search_google(query)

    return None


# ============================================================
# COMMAND DETECTION
# ============================================================

def can_handle(command: str) -> bool:
    """
    Tell the Nexus skill router whether this skill
    understands the command.
    """

    command = clean_command(command)

    if not command:
        return False

    # --------------------------------------------------------
    # YouTube actions
    # --------------------------------------------------------

    youtube_starters = [
        "play ",
        "watch ",
        "find on youtube ",
        "search youtube ",
        "search youtube for ",
        "look up on youtube ",
        "find youtube ",
    ]

    if any(
        command.startswith(x)
        for x in youtube_starters
    ):
        return True

    # --------------------------------------------------------
    # Google / Web search
    # --------------------------------------------------------

    google_starters = [
        "search google ",
        "search google for ",
        "google search ",
        "google search for ",
        "search the web ",
        "search web ",
        "search the internet ",
        "look up on google ",
        "find on google ",
        "search ",
        "find ",
        "look up ",
    ]

    if any(
        command.startswith(x)
        for x in google_starters
    ):
        return True

    # --------------------------------------------------------
    # Website navigation
    # --------------------------------------------------------

    navigation_words = [
        "open ",
        "launch ",
        "go to ",
        "take me to ",
        "visit ",
        "navigate to ",
    ]

    if any(
        command.startswith(x)
        for x in navigation_words
    ):

        for website in WEBSITES:

            if website in command:
                return True

    # Direct website name
    if command in WEBSITES:
        return True

    return False


# ============================================================
# MAIN COMMAND HANDLER
# ============================================================

def handle(command: str) -> str:
    """
    Main entry point used by Nexus.
    """

    command = clean_command(command)

    if not command:
        return "I didn't hear a browser command."

    # ========================================================
    # 1. YOUTUBE ACTIONS
    # ========================================================

    result = handle_youtube_action(command)

    if result:
        return result

    # ========================================================
    # 2. GOOGLE / WEB SEARCH
    # ========================================================

    result = handle_google_search(command)

    if result:
        return result

    # ========================================================
    # 3. GENERIC SEARCH
    # ========================================================

    result = handle_generic_search(command)

    if result:
        return result

    # ========================================================
    # 4. OPEN WEBSITE
    # ========================================================

    return open_website(command)


# ============================================================
# END OF NEXUS BROWSER SKILL
# ============================================================
