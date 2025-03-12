import base64
import cv2
import numpy as np
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from io import BytesIO
from PIL import Image
import logging

# Import our FaceMonitor and SoundMonitor classes
from .face_monitor import FaceMonitor
from .sound_monitor import SoundMonitor

logger = logging.getLogger(__name__)

face_monitor = FaceMonitor()
sound_monitor = SoundMonitor()

@login_required
def index(request):
    return render(request, 'integrity_app/index.html')

@login_required
@csrf_exempt
def process_frame(request):
    if request.method == 'POST':
        data = request.POST.get('image')
        if data:
            try:
                # Expecting a base64-encoded JPEG image (e.g., "data:image/jpeg;base64,...")
                header, encoded = data.split(',', 1)
                img_bytes = base64.b64decode(encoded)
                img = Image.open(BytesIO(img_bytes))
                img_array = np.array(img)
                # Convert RGB (PIL) to BGR (OpenCV)
                frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                processed_frame = face_monitor.analyze_face(frame)
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                return JsonResponse({
                    'processed_image': f'data:image/jpeg;base64,{jpg_as_text}',
                    'face_status': face_monitor.current_status
                })
            except Exception as e:
                logger.exception("Error processing frame")
                return JsonResponse({'error': f'Error processing frame: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def process_audio(request):
    if request.method == 'POST':
        data = request.POST.get('audio')
        if data:
            try:
                # Log the received data length for debugging
                logger.info("Received audio data length: %s", len(data))
                header, encoded = data.split(',', 1)
                audio_bytes = base64.b64decode(encoded)
                logger.info("Decoded audio bytes length: %s", len(audio_bytes))
                result = sound_monitor.process_audio_chunk(audio_bytes)
                logger.info("Recognized texts: %s", result['recognized_texts'])
                return JsonResponse({
                    'recognized_texts': result['recognized_texts'],
                    'violation_found': result['violation_found']
                })
            except Exception as e:
                logger.exception("Error processing audio")
                return JsonResponse({'error': f'Error processing audio: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)