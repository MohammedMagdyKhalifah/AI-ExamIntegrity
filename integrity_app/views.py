import base64
import os
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pydub import AudioSegment
import speech_recognition as sr

from accounts.decorators import student_required, proctor_required
from .monitoring import FaceMonitor

logger = logging.getLogger(__name__)

# Single FaceMonitor instance
face_monitor = FaceMonitor()

# Pick best device and (for CUDA) set it
if torch.cuda.is_available():
    device = 'cuda:0'
    torch.cuda.set_device(0)
elif torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'

# Load YOLOv8 model once, then move it to our device
YOLO_WEIGHTS = settings.BASE_DIR / 'models' / 'best.pt'
object_detector = YOLO(YOLO_WEIGHTS)  # no device= here!
object_detector.to(device)            # now it's on GPU/MPS/CPU


@student_required
def index(request):
    return render(request, 'integrity_app/student_dashboard.html')


@student_required
@csrf_exempt
def process_frame(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Decode incoming base64 frame
    image_data = request.POST.get('image', '')
    try:
        _, encoded = image_data.split(',', 1)
        frame = cv2.imdecode(
            np.frombuffer(base64.b64decode(encoded), np.uint8),
            cv2.IMREAD_COLOR
        )
    except Exception as e:
        logger.error("Bad image data: %s", e)
        return JsonResponse({'error': 'Bad image data'}, status=400)

    # Define the two tasks
    def face_task():
        return face_monitor.analyze_face(frame.copy())

    def detect_task():
        # You can also pass device here if you like:
        # return object_detector(frame.copy(), device=device)[0]
        return object_detector(frame.copy())[0]

    # Run them in parallel
    with ThreadPoolExecutor(max_workers=2) as exe:
        future_face = exe.submit(face_task)
        future_det  = exe.submit(detect_task)
        face_img    = future_face.result()
        det_result  = future_det.result()

    # Build detection list
    detections = []
    names = object_detector.names
    for box, cls, conf in zip(
        det_result.boxes.xyxy.tolist(),
        det_result.boxes.cls.tolist(),
        det_result.boxes.conf.tolist()
    ):
        x1, y1, x2, y2 = map(int, box)
        detections.append({
            'box':       [x1, y1, x2, y2],
            'class_id':  int(cls),
            'class_name': names[int(cls)],
            'confidence': float(conf),
        })

    # Encode face-monitor output
    _, buf_face = cv2.imencode('.jpg', face_img)
    face_b64    = base64.b64encode(buf_face).decode('utf-8')
    face_url    = 'data:image/jpeg;base64,' + face_b64

    # Annotate original frame for objects
    obj_img = frame.copy()
    for d in detections:
        x1, y1, x2, y2 = d['box']
        cv2.rectangle(obj_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            obj_img,
            f"{d['class_name']}:{d['confidence']:.2f}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 255, 0), 1
        )

    _, buf_obj = cv2.imencode('.jpg', obj_img)
    obj_b64    = base64.b64encode(buf_obj).decode('utf-8')
    obj_url    = 'data:image/jpeg;base64,' + obj_b64

    return JsonResponse({
        'face_image':   face_url,
        'face_status':  face_monitor.current_status,
        'object_image': obj_url,
        'detections':   detections,
    })


@student_required
@csrf_exempt
def process_audio(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # Save WebM
    audio_data = request.body
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    webm_fp = os.path.join(settings.MEDIA_ROOT, f"recording_{ts}.webm")
    os.makedirs(os.path.dirname(webm_fp), exist_ok=True)
    try:
        with open(webm_fp, "wb") as f:
            f.write(audio_data)
        logger.info("Saved WebM: %s", webm_fp)
    except Exception as e:
        logger.error("Error saving WebM: %s", e)
        return JsonResponse({'status':'failure','feedback':"Failed to save recording."})

    # Convert to MP3 (with fallbacks)
    try:
        audio = AudioSegment.from_file(webm_fp)
    except Exception as e1:
        logger.warning("Autodetect failed: %s", e1)
        for fmt in ("ogg","opus"):
            try:
                audio = AudioSegment.from_file(webm_fp, format=fmt)
                break
            except Exception as e2:
                logger.warning("%s failed: %s", fmt, e2)
        else:
            return JsonResponse({'status':'failure','feedback':"Failed to convert to MP3."})

    mp3_fp = os.path.join(settings.MEDIA_ROOT, f"recording_{ts}.mp3")
    try:
        audio.export(mp3_fp, format="mp3")
        logger.info("Exported MP3: %s", mp3_fp)
    except Exception as e:
        logger.error("Error exporting MP3: %s", e)
        return JsonResponse({'status':'failure','feedback':"Failed to export MP3."})

    # Cleanup WebM
    try: os.remove(webm_fp)
    except: pass

    # MP3 → WAV
    wav_fp = os.path.join(settings.MEDIA_ROOT, f"recording_{ts}.wav")
    try:
        AudioSegment.from_file(mp3_fp, format="mp3").export(wav_fp, format="wav")
        logger.info("Exported WAV: %s", wav_fp)
    except Exception as e:
        logger.error("Error exporting WAV: %s", e)
        return JsonResponse({'status':'failure','feedback':"Failed to convert to WAV."})

    # Speech recognition
    rec = sr.Recognizer()
    try:
        with sr.AudioFile(wav_fp) as src:
            audio_file = rec.record(src)
        text_en = rec.recognize_google(audio_file, language="en")
        text_ar = rec.recognize_google(audio_file, language="ar")
        logger.info("EN: %s | AR: %s", text_en, text_ar)
    except sr.UnknownValueError:
        text_en = "Could not understand English."
        text_ar = "Could not understand Arabic."
    except sr.RequestError as e:
        text_en = "Google API error (EN)."
        text_ar = "Google API error (AR)."
        logger.error("Speech API error: %s", e)
    except Exception as e:
        logger.error("General SR error: %s", e)
        return JsonResponse({'status':'failure','feedback':"Error during speech recognition."})

    # Cleanup WAV
    try: os.remove(wav_fp)
    except: pass

    feedback = (
        f"Recording saved! (MP3: recording_{ts}.mp3)\n\n"
        f"English: {text_en}\n\n"
        f"Arabic: {text_ar}"
    )
    return JsonResponse({'status':'success','feedback': feedback})
