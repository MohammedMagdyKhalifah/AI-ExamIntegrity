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
from accounts.decorators import student_required, proctor_required


# Import our FaceMonitor and SoundMonitor classes
from .monitoring import FaceMonitor, SoundMonitor


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

# @student_required
# @csrf_exempt
# def process_audio(request):
#     if request.method == 'POST':
#         data = request.POST.get('audio')
#         if data:
#             try:
#                 # Log the received data length for debugging
#                 logger.info("Received audio data length: %s", len(data))
#                 header, encoded = data.split(',', 1)
#                 audio_bytes = base64.b64decode(encoded)
#                 logger.info("Decoded audio bytes length: %s", len(audio_bytes))
#                 result = sound_monitor.process_audio_chunk(audio_bytes)
#                 logger.info("Recognized texts: %s", result['recognized_texts'])
#                 return JsonResponse({
#                     'recognized_texts': result['recognized_texts'],
#                     'violation_found': result['violation_found']
#                 })
#             except Exception as e:
#                 logger.exception("Error processing audio")
#                 return JsonResponse({'error': f'Error processing audio: {str(e)}'}, status=500)
#     return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST':
        audio_data = request.POST.get('audio')
        if audio_data:
            header, encoded = audio_data.split(',', 1)
            audio_bytes = base64.b64decode(encoded)
            sound_monitor = SoundMonitor()
            result = sound_monitor.process_audio_chunk(audio_bytes)
            return JsonResponse(result)
    return JsonResponse({'error': 'Invalid request'}, status=400)