import base64
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pydub import AudioSegment
import speech_recognition as sr
from django.conf import settings

logger = logging.getLogger(__name__)


class FrameAnalyzer:
    """
    Handles face monitoring and object detection on video frames.
    """
    def __init__(self, weights_path: Path, face_monitor):
        self.face_monitor = face_monitor
        self.device = self._select_device()
        # Load YOLO and move to correct device
        self.model = YOLO(str(weights_path))
        self.model.to(self.device)

    def _select_device(self) -> str:
        if torch.cuda.is_available():
            torch.cuda.set_device(0)
            return "cuda:0"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _run_face(self, frame: np.ndarray) -> np.ndarray:
        return self.face_monitor.analyze_face(frame)

    def _run_object(self, frame: np.ndarray):
        # run inference on selected device
        return self.model(frame, device=self.device)[0]

    def _encode_image(self, img: np.ndarray) -> str:
        _, buf = cv2.imencode('.jpg', img)
        b64 = base64.b64encode(buf).decode('utf-8')
        return f"data:image/jpeg;base64,{b64}"

    def analyze(self, frame: np.ndarray) -> dict:
        # Run face and object detection in parallel
        with ThreadPoolExecutor(max_workers=2) as exe:
            f_face = exe.submit(self._run_face, frame.copy())
            f_obj  = exe.submit(self._run_object, frame.copy())
            face_img   = f_face.result()
            det_result = f_obj.result()

        # Parse detections
        detections = []
        names = self.model.names
        for box, cls, conf in zip(
            det_result.boxes.xyxy.tolist(),
            det_result.boxes.cls.tolist(),
            det_result.boxes.conf.tolist()
        ):
            x1, y1, x2, y2 = map(int, box)
            detections.append({
                'box': [x1, y1, x2, y2],
                'class_id': int(cls),
                'class_name': names[int(cls)],
                'confidence': float(conf),
            })

        # Encode face image
        face_url = self._encode_image(face_img)

        # Annotate and encode object image
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
        object_url = self._encode_image(obj_img)

        return {
            'face_image':   face_url,
            'face_status':  self.face_monitor.current_status,
            'object_image': object_url,
            'detections':   detections,
        }


class AudioAnalyzer:
    """
    Handles saving, format-conversion, and speech recognition for audio streams.
    """
    def __init__(self, media_root: Path):
        self.media_root = media_root

    def _save_temp(self, data: bytes, prefix: str, ext: str) -> Path:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.media_root / f"{prefix}_{ts}.{ext}"
        fp.parent.mkdir(parents=True, exist_ok=True)
        with open(fp, "wb") as f:
            f.write(data)
        return fp

    def process(self, webm_bytes: bytes) -> dict:
        # Save WebM
        try:
            webm_fp = self._save_temp(webm_bytes, 'recording', 'webm')
        except Exception as e:
            logger.error("Saving WebM failed: %s", e)
            return {'status':'failure','feedback':'Failed to save recording.'}

        # Convert WebM to MP3 with fallbacks
        try:
            audio = AudioSegment.from_file(webm_fp)
        except Exception:
            audio = None
            for fmt in ('ogg', 'opus'):
                try:
                    audio = AudioSegment.from_file(webm_fp, format=fmt)
                    break
                except Exception:
                    pass
            if audio is None:
                return {'status':'failure','feedback':'Failed to convert to MP3.'}

        # Export MP3 (and keep it)
        mp3_fp = webm_fp.with_suffix('.mp3')
        try:
            audio.export(mp3_fp, format='mp3')
        except Exception as e:
            logger.error("MP3 export failed: %s", e)
            return {'status':'failure','feedback':'Failed to export MP3.'}

        # Build the media URL for the MP3
        mp3_url = settings.MEDIA_URL.rstrip('/') + '/' + mp3_fp.name

        # Remove original WebM
        try:
            webm_fp.unlink()
        except:
            pass

        # Convert MP3 → WAV
        wav_fp = mp3_fp.with_suffix('.wav')
        try:
            AudioSegment.from_file(mp3_fp, format='mp3').export(wav_fp, format='wav')
        except Exception as e:
            logger.error("WAV conversion failed: %s", e)
            return {'status':'failure','feedback':'Failed to convert to WAV.'}

        # Speech recognition
        rec = sr.Recognizer()
        try:
            with sr.AudioFile(str(wav_fp)) as src:
                audio_file = rec.record(src)
            text_en = rec.recognize_google(audio_file, language='en')
            text_ar = rec.recognize_google(audio_file, language='ar')
        except sr.UnknownValueError:
            text_en = 'Could not understand English.'
            text_ar = 'Could not understand Arabic.'
        except sr.RequestError as e:
            logger.error('Speech API error: %s', e)
            text_en = 'Google API error (EN).'
            text_ar = 'Google API error (AR).'
        except Exception as e:
            logger.error('General SR error: %s', e)
            return {'status':'failure','feedback':'Error during speech recognition.'}

        # Cleanup WAV
        try:
            wav_fp.unlink()
        except:
            pass

        feedback = (
            f"Recording saved! MP3 available at: {mp3_url}\n\n"
            f"English: {text_en}\n\n"
            f"Arabic: {text_ar}"
        )
        return {'status':'success','feedback': feedback, 'mp3_url': mp3_url}
