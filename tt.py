import pyttsx3

engine = pyttsx3.init()  # Initialize the engine

try:
    engine.say("This is a pyttsx3 test.")
    engine.runAndWait()
    print("TTS test complete.")  # Print a message to confirm
except Exception as e:
    print(f"pyttsx3 error: {e}") # Print any pyttsx3 errors