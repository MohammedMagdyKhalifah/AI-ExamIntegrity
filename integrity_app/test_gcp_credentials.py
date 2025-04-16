import os
from google.cloud import speech

def main():
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        print("GOOGLE_APPLICATION_CREDENTIALS is not set!")
        return
    print("Using credentials file:", credentials_path)
    try:
        client = speech.SpeechClient()
        print("Google Cloud Speech Client created successfully.")
    except Exception as e:
        print("Failed to create Speech Client:", e)

if __name__ == "__main__":
    main()