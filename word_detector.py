import speech_recognition as sr

# Set the keyword you want to detect
TARGET_WORD = "hello"

def recognize_speech():
    print("🔄 Function started: recognize_speech()")  # Debugging line
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening for 3 seconds... Speak now!")
        
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            print("🎙️ Audio recorded successfully!")  # Debugging line
        except sr.WaitTimeoutError:
            print("⚠️ No speech detected, try again.")
            return None

    try:
        print("⏳ Sending audio to Google for processing...")  # Debugging line
        text = recognizer.recognize_google(audio)
        print(f"📝 Recognized Speech: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("⚠️ Could not understand the audio.")
        return None
    except sr.RequestError:
        print("⚠️ Error with speech recognition service.")
        return None

def detect_target_word(text):
    print("🔄 Function started: detect_target_word()")  # Debugging line
    if text and TARGET_WORD in text:
        print(f"✅ ALERT! The word '{TARGET_WORD}' was detected!")
    else:
        print("❌ No target word detected.")

if __name__ == "__main__":
    print("🚀 Script started!")  # Debugging line
    spoken_text = recognize_speech()
    detect_target_word(spoken_text)
