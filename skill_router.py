# ============================================================
# NEXUS SKILL ROUTER
# ============================================================
#
# Architecture:
#
# User voice
#     ↓
# Nexus
#     ↓
# Local skills
#     ↓
# Ollama natural-language planner
#     ↓
# Computer skill
#     ↓
# Gemini fallback
#
# ============================================================


from skills import computer
from skills import browser
from skills import system
from skills import spotify
from skills import files

from local_ai import understand


# ============================================================
# LOCAL SKILLS
# ============================================================

LOCAL_SKILLS = [
    computer,
    browser,
    system,
    spotify,
    files,
]


# ============================================================
# TRY EXISTING LOCAL SKILLS
# ============================================================

def try_local_skills(command: str):

    for skill in LOCAL_SKILLS:

        try:

            if skill.can_handle(command):

                print(
                    f"🛠️ Local skill: "
                    f"{skill.__name__}"
                )

                response = skill.handle(command)

                return response

        except Exception as exc:

            print(
                f"❌ Skill error "
                f"{skill.__name__}: {exc}"
            )

    return None


# ============================================================
# HANDLE COMMAND
# ============================================================

def handle(command: str):

    command = command.strip()

    if not command:
        return None


    # ========================================================
    # STEP 1
    # EXISTING LOCAL SKILLS
    # ========================================================

    print("🔎 Checking local skills...")

    response = try_local_skills(command)

    if response:

        print(
            f"⚡ Local skill handled it."
        )

        return response


    # ========================================================
    # STEP 2
    # OLLAMA NATURAL-LANGUAGE UNDERSTANDING
    # ========================================================

    print(
        "🧠 Understanding naturally with local AI..."
    )

    try:

        planned_command = understand(command)

    except Exception as exc:

        print(
            f"❌ Local AI error: {exc}"
        )

        planned_command = None


    # ========================================================
    # STEP 3
    # EXECUTE OLLAMA PLAN
    # ========================================================

    if planned_command:

        print(
            f"⚡ Local AI plan: "
            f"{planned_command}"
        )

        try:

            response = computer.handle(
                planned_command
            )

            if response:

                print(
                    f"🖥️ Computer action complete."
                )

                return response

        except Exception as exc:

            print(
                f"❌ Computer execution error: "
                f"{exc}"
            )


    # ========================================================
    # STEP 4
    # RETURN NONE
    #
    # nexus.py will send this to Gemini.
    # ========================================================

    print(
        "🤖 No local computer action found."
    )

    return None
