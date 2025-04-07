import cv2
import mediapipe as mp
import time
import numpy as np
import speech_recognition as sr
import subprocess
import tempfile
import io

# -----------------------
# Face Monitor Class
# -----------------------

class FaceMonitor:
    def __init__(self):
        self.face_mesh_module = mp.solutions.face_mesh
        self.face_mesh = self.face_mesh_module.FaceMesh(refine_landmarks=True)
        self.drawing_utils = mp.solutions.drawing_utils

        self.suspicious_threshold = 1.5  # seconds before alerting
        self.center_tolerance = 0.10       # acceptable deviation from center

        self.last_normal_time = time.time()
        self.suspicious_active = False
        self.current_status = "Normal Behavior"

    def track_gaze(self, landmarks):
        eyes_ok = self._check_eye_gaze(landmarks)
        head_ok = self._check_head_movement(landmarks)
        return eyes_ok and head_ok

    def detect_violation(self, frame, landmarks):
        is_normal = self.track_gaze(landmarks)
        if not is_normal:
            if not self.suspicious_active:
                self.last_normal_time = time.time()
                self.suspicious_active = True
            elif time.time() - self.last_normal_time > self.suspicious_threshold:
                self.annotate_alert(frame, f"Suspicious: {self.current_status}")
        else:
            self.suspicious_active = False

        cv2.putText(frame, self.current_status, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    def annotate_alert(self, frame, message):
        cv2.putText(frame, message, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def analyze_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.drawing_utils.draw_landmarks(
                    frame, face_landmarks, self.face_mesh_module.FACEMESH_TESSELATION
                )
                frame = self.detect_violation(frame, face_landmarks.landmark)
        return frame

    def _check_eye_gaze(self, landmarks):
        left_eye_outer = landmarks[33]
        right_eye_outer = landmarks[263]
        left_eye_inner = landmarks[133]
        right_eye_inner = landmarks[362]

        mid_x = (left_eye_outer.x + right_eye_outer.x) / 2
        horizontal_deviation = abs(mid_x - 0.5)
        if horizontal_deviation > self.center_tolerance:
            self.current_status = "Brief: Looking Left" if mid_x < 0.5 else "Brief: Looking Right"
            return False
        else:
            avg_y = (left_eye_inner.y + right_eye_inner.y) / 2
            center_y = 0.5
            if avg_y < center_y - 0.15:
                self.current_status = "Brief: Looking Up"
                return False
            elif avg_y > center_y + 0.10:
                self.current_status = "Fully Acceptable: Looking Down"
                return True
            else:
                self.current_status = "Normal Behavior"
                return True

    def _check_head_movement(self, landmarks):
        nose = landmarks[1]
        if abs(nose.x - 0.5) > self.center_tolerance:
            self.current_status = "Brief: Head Rotated Left" if nose.x < 0.5 else "Brief: Head Rotated Right"
            return False
        if nose.y < 0.4:
            self.current_status = "Brief: Head Moved Up"
            return False
        elif nose.y > 0.6:
            self.current_status = "Fully Acceptable: Head Moved Down"
            return True
        self.current_status = "Normal Behavior"
        return True

    def process_frame(self, frame_bytes):
        """
        Process a frame from bytes data sent by the client.
        Returns a dictionary with the current status, a flag for suspicious behavior,
        and the processed frame data (JPEG bytes).
        """
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        processed_frame = self.analyze_face(frame)
        retval, buffer = cv2.imencode('.jpg', processed_frame)
        processed_bytes = buffer.tobytes()
        return {
            "status": self.current_status,
            "is_suspicious": self.suspicious_active and (time.time() - self.last_normal_time > self.suspicious_threshold),
            "frame_data": processed_bytes
        }

# -----------------------
# Sound Monitor Class
# -----------------------

class SoundMonitor:
    def __init__(self, languages=None):
        self.recognizer = sr.Recognizer()
        self.languages = languages if languages is not None else {"English": "en", "Arabic": "ar"}
        self.suspicious_words = [
            "غش", "مساعدة", "ساعدني", "حل", "cheat", "cheating", "help", "answers",
            "google", "copy", "الاجابه", "الاجابة", "اختار الاجابة", "الاختيار", "اختار",
            "answer", "حلها", "سؤال", "السؤال", "شابتر", "الشابتر", "chapter"
        ]

    def convert_ogg_to_wav(self, audio_bytes):
        """
        Converts an OGG audio file (from the client) to WAV.
        Writes the raw audio data to a temporary file and calls ffmpeg.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as temp_input:
                temp_input.write(audio_bytes)
                temp_input.flush()
                result = subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel", "error",
                        "-y",
                        "-i", temp_input.name,
                        "-f", "wav",
                        "pipe:1"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                return result.stdout
        except subprocess.CalledProcessError as e:
            print("Error converting OGG to WAV:", e.stderr.decode())
            return None

    def process_audio_chunk(self, audio_bytes, sample_rate=16000, sample_width=2):
        """
        Processes a chunk of audio data.
        Converts incoming OGG audio to WAV and transcribes it.
        Returns a dictionary with recognized texts and a violation flag.
        """
        wav_bytes = self.convert_ogg_to_wav(audio_bytes)
        if wav_bytes is None:
            wav_bytes = audio_bytes

        recognized_texts = {}
        violation_found = False

        try:
            audio_data = sr.AudioData(wav_bytes, sample_rate, sample_width)
        except Exception as e:
            print("Error creating AudioData:", str(e))
            return {
                "recognized_texts": {"English": "[Error]", "Arabic": "[Error]"},
                "violation_found": False
            }

        for lang, code in self.languages.items():
            try:
                text = self.recognizer.recognize_google(audio_data, language=code)
            except sr.UnknownValueError:
                text = ""
            except sr.RequestError:
                text = "[ERROR: Recognition service unavailable]"

            if not text.strip():
                text = "No speech recognized" if lang == "English" else "لم يتم التعرف على الكلام"
            recognized_texts[lang] = text

            for suspicious_word in self.suspicious_words:
                if suspicious_word.lower() in text.lower():
                    violation_found = True

        return {
            "recognized_texts": recognized_texts,
            "violation_found": violation_found
        }