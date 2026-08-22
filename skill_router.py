from skills import spotify
from skills import browser
from skills import system
from skills import files
from skills import search

SKILLS = [
    spotify,
    browser,
    system,
    files,
    search,

]


def handle(command: str):
    """
    Try every registered skill.

    Returns:
        response string if a skill handled it
        None if Gemini should handle it
    """

    for skill in SKILLS:

        try:
            if skill.can_handle(command):
                return skill.handle(command)

        except Exception as exc:
            print(
                f"❌ Skill error "
                f"{skill.__name__}: {exc}"
            )

    return None

