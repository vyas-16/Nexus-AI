import speech_recognition as sr

recognizer = sr.Recognizer()

print("🎤 Nexon is listening...")
print("Say something...")

with sr.Microphone(device_index=0) as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

print("🧠 Processing...")

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)
except sr.UnknownValueError:
    print("Nexon couldn't understand that.")
except sr.RequestError as e:
    print("Speech recognition service error:", e)
except Exception as e:
    print("Error:", e)
