from pynput import keyboard
import threading
from nexus import run_voice_session

busy = False
lock = threading.Lock()


def activate_nexus():
    global busy

    with lock:
        if busy:
            print("⏳ Nexus is already listening...")
            return
        busy = True

    try:
        print("\n⚡ NEXUS ACTIVATED")
        run_voice_session()
    except Exception as e:
        print(f"❌ Nexus error: {e}")
    finally:
        busy = False
        print("💤 Nexus is ready.")


def on_activate():
    threading.Thread(
        target=activate_nexus,
        daemon=True
    ).start()


print("================================")
print("        🤖 NEXUS CONTROLLER")
print("================================")
print("⌘ + Shift + N  →  Activate Nexus")
print("Ctrl+C         →  Stop")
print()

with keyboard.GlobalHotKeys({
    '<cmd>+<shift>+n': on_activate
}) as listener:
    try:
        listener.join()
    except KeyboardInterrupt:
        print("\n Nexus controller Stopped!")

