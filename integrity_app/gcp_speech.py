from google.cloud import speech


def gcp_speech_to_text(audio_bytes, sample_rate=16000, language_code='en-US'):
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Changed to LINEAR16
        sample_rate_hertz=sample_rate,
        language_code=language_code,
        enable_automatic_punctuation=True
    )

    try:
        response = client.recognize(config=config, audio=audio)
        return " ".join(
            result.alternatives[0].transcript
            for result in response.results
        ).strip()

    except Exception as e:
        return f"Transcription Error: {str(e)}"