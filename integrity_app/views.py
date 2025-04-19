import base64
import cv2
import numpy as np
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from accounts.decorators import student_required
from .monitoring import FaceMonitor
from .analyzers import FrameAnalyzer, AudioAnalyzer

# Set up once
MODEL_PATH      = Path(settings.BASE_DIR) / 'models' / 'best.pt'
frame_analyzer  = FrameAnalyzer(MODEL_PATH, FaceMonitor())
audio_analyzer  = AudioAnalyzer(Path(settings.MEDIA_ROOT))

@student_required
def index(request):
    return render(request, 'integrity_app/student_dashboard.html')

@student_required
@csrf_exempt
def process_frame(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid request'}, status=400)

    data_url = request.POST.get('image','')
    try:
        _, b64 = data_url.split(',',1)
        frame = cv2.imdecode(
            np.frombuffer(base64.b64decode(b64), np.uint8),
            cv2.IMREAD_COLOR
        )
    except Exception:
        return JsonResponse({'error':'Bad image data'}, status=400)

    result = frame_analyzer.analyze(frame)
    return JsonResponse(result)

@student_required
@csrf_exempt
def process_audio(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Invalid request method'}, status=405)

    return JsonResponse(audio_analyzer.process(request.body))
