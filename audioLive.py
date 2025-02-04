import speech_recognition as sr

rec = sr.Recognizer()

# Using the microphone as input source
with sr.Microphone() as src:
    rec.adjust_for_ambient_noise(src)  # Adjusts for background noise
    print("Say something in English or Arabic...")

    while True:
        try:
            audio = rec.listen(src)  # Listen to the microphone
            
            # Recognize speech (change 'ar' to 'en' or other languages)
            text_en = rec.recognize_google(audio, language="en")  # English
            text_ar = rec.recognize_google(audio, language="ar")  # Arabic
            
            print("English:", text_en)
            print("Arabic:", text_ar)

        except sr.UnknownValueError:
            print("Could not understand the audio. Please try again.")
        
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition. Check your internet connection.")