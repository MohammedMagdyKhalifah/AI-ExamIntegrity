import base64
import os
import datetime
from django.conf import settings
from pydub import AudioSegment

import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import logging
from accounts.decorators import student_required, proctor_required
import speech_recognition as sr

from .monitoring import FaceMonitor

logger = logging.getLogger(__name__)


@student_required
def index(request):
    return render(request, 'integrity_app/student_dashboard.html')

# Create a single instance of FaceMonitor for processing frames
face_monitor = FaceMonitor()

@student_required
@csrf_exempt
def process_frame(request):
    if request.method == 'POST':
        image_data = request.POST.get('image')
        if image_data:
            # image_data is expected as data URL: "data:image/jpeg;base64,..."
            header, encoded = image_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            processed_img = face_monitor.analyze_face(img)
            retval, buffer = cv2.imencode('.jpg', processed_img)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            return JsonResponse({
                'processed_image': 'data:image/jpeg;base64,' + jpg_as_text,
                'face_status': face_monitor.current_status,
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@student_required
@csrf_exempt
def process_audio(request):
    """
    Receives binary audio data (expected as WebM from the browser),
    saves it to disk, converts it to MP3 (with autodetection and fallback),
    removes the original WebM file, converts the MP3 to a temporary WAV file for
    speech recognition, processes the audio in both English and Arabic,
    and returns feedback with the recognized texts.
    """
    if request.method == 'POST':
        # Save the incoming audio data as a file.
        audio_data = request.body
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        webm_file_name = f"recording_{timestamp}.webm"
        webm_file_path = os.path.join(settings.MEDIA_ROOT, webm_file_name)
        os.makedirs(os.path.dirname(webm_file_path), exist_ok=True)
        try:
            with open(webm_file_path, "wb") as f:
                f.write(audio_data)
            logger.info("Audio saved as WebM at: %s", webm_file_path)
        except Exception as e:
            logger.error("Error saving audio file: %s", e)
            return JsonResponse({'status': 'failure', 'feedback': "Failed to save recording."})

        # Convert the file to MP3.
        try:
            # First attempt: let pydub autodetect the format.
            audio = AudioSegment.from_file(webm_file_path)
        except Exception as e_autodetect:
            logger.error("Autodetection conversion failed: %s", e_autodetect)
            try:
                # Second attempt: try assuming an Ogg container.
                audio = AudioSegment.from_file(webm_file_path, format="ogg")
            except Exception as e_ogg:
                logger.error("Conversion with 'ogg' format failed: %s", e_ogg)
                try:
                    # Third attempt: try using "opus" as the container.
                    audio = AudioSegment.from_file(webm_file_path, format="opus")
                except Exception as e_opus:
                    logger.error("Conversion with 'opus' format failed: %s", e_opus)
                    return JsonResponse({
                        'status': 'failure',
                        'feedback': "Recording saved but failed to convert to MP3."
                    })

        mp3_file_name = f"recording_{timestamp}.mp3"
        mp3_file_path = os.path.join(settings.MEDIA_ROOT, mp3_file_name)
        try:
            audio.export(mp3_file_path, format="mp3")
            logger.info("Audio converted and saved as MP3 at: %s", mp3_file_path)
        except Exception as e_export:
            logger.error("Error exporting MP3: %s", e_export)
            return JsonResponse({
                'status': 'failure',
                'feedback': "Recording saved but failed to export MP3."
            })

        # Remove the original file.
        try:
            os.remove(webm_file_path)
            logger.info("Removed original file: %s", webm_file_path)
        except Exception as e_rm:
            logger.warning("Could not remove original file: %s", e_rm)

        # Convert the MP3 file to a temporary WAV file for speech recognition.
        wav_file_name = f"recording_{timestamp}.wav"
        wav_file_path = os.path.join(settings.MEDIA_ROOT, wav_file_name)
        try:
            mp3_audio = AudioSegment.from_file(mp3_file_path, format="mp3")
            mp3_audio.export(wav_file_path, format="wav")
            logger.info("Converted MP3 to temporary WAV at: %s", wav_file_path)
        except Exception as e_wav:
            logger.error("Error converting MP3 to WAV: %s", e_wav)
            return JsonResponse({
                'status': 'failure',
                'feedback': "Recording saved but failed to convert MP3 to WAV for recognition."
            })

        # Run speech recognition on the WAV file.
        rec = sr.Recognizer()
        recognized_text_en = ""
        recognized_text_ar = ""
        try:
            with sr.AudioFile(wav_file_path) as source:
                audio_file = rec.record(source)
            recognized_text_en = rec.recognize_google(audio_file, language="en")
            recognized_text_ar = rec.recognize_google(audio_file, language="ar")
            logger.info("Speech recognition succeeded: English: %s, Arabic: %s", recognized_text_en, recognized_text_ar)
        except sr.UnknownValueError:
            recognized_text_en = "Could not understand the audio in English."
            recognized_text_ar = "Could not understand the audio in Arabic."
            logger.warning("Speech recognition could not understand the audio.")
        except sr.RequestError as e_req:
            recognized_text_en = "Could not request results from Google for English."
            recognized_text_ar = "Could not request results from Google for Arabic."
            logger.error("Speech recognition request error: %s", e_req)
        except Exception as e_recog:
            logger.error("General error during speech recognition: %s", e_recog)
            return JsonResponse({
                'status': 'failure',
                'feedback': "Error during speech recognition."
            })

        # Remove the temporary WAV file.
        try:
            os.remove(wav_file_path)
            logger.info("Removed temporary WAV file: %s", wav_file_path)
        except Exception as e_rm_wav:
            logger.warning("Could not remove temporary WAV file: %s", e_rm_wav)

        feedback = (
            f"Recording saved successfully! (MP3: {mp3_file_name})\n\n"
            f"English: {recognized_text_en}\n\n"
            f"Arabic: {recognized_text_ar}"
        )
        return JsonResponse({'status': 'success', 'feedback': feedback})

    return JsonResponse({'error': 'Invalid request method'}, status=405)