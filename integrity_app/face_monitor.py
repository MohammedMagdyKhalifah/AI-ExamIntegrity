import cv2
import mediapipe as mp
import time

class FaceMonitor:
    def __init__(self):
        # Initialize mediapipe's face mesh with refined landmarks for improved accuracy
        self.face_mesh_module = mp.solutions.face_mesh
        self.face_mesh = self.face_mesh_module.FaceMesh(refine_landmarks=True)
        self.drawing_utils = mp.solutions.drawing_utils

        # Configuration thresholds
        self.suspicious_threshold = 1.5  # seconds before alerting
        self.center_tolerance = 0.10       # acceptable deviation from center

        # Timing and status tracking
        self.last_normal_time = time.time()
        self.suspicious_active = False
        self.current_status = "Normal Behavior"

    def track_gaze(self, landmarks):
        """
        Evaluates both eye gaze and head position.
        Returns True if both are within acceptable limits, else False.
        """
        eyes_ok = self._check_eye_gaze(landmarks)
        head_ok = self._check_head_movement(landmarks)
        return eyes_ok and head_ok

    def detect_violation(self, frame, landmarks):
        """
        Analyzes face landmarks to detect suspicious behavior.
        If abnormal behavior persists beyond the threshold, an alert is annotated on the frame.
        """
        is_normal = self.track_gaze(landmarks)
        if not is_normal:
            if not self.suspicious_active:
                self.last_normal_time = time.time()
                self.suspicious_active = True
            elif time.time() - self.last_normal_time > self.suspicious_threshold:
                self.annotate_alert(frame, f"Suspicious: {self.current_status}")
        else:
            self.suspicious_active = False

        # Overlay the current status on the frame
        cv2.putText(frame, self.current_status, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

    def annotate_alert(self, frame, message):
        """
        Overlays an alert message on the video frame.
        """
        cv2.putText(frame, message, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def analyze_face(self, frame):
        """
        Processes a video frame: detects face landmarks, checks for violations, and annotates the frame accordingly.
        """
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
        """
        Checks the eye landmarks to determine gaze direction.
        Uses landmarks 33 and 263 for horizontal assessment, and 133 and 362 for vertical direction.
        """
        left_eye_outer = landmarks[33]
        right_eye_outer = landmarks[263]
        left_eye_inner = landmarks[133]
        right_eye_inner = landmarks[362]

        # Calculate horizontal midpoint and deviation
        mid_x = (left_eye_outer.x + right_eye_outer.x) / 2
        horizontal_deviation = abs(mid_x - 0.5)

        if horizontal_deviation > self.center_tolerance:
            if mid_x < 0.5:
                self.current_status = "Brief: Looking Left"
            else:
                self.current_status = "Brief: Looking Right"
            return False
        else:
            # Evaluate vertical gaze using inner eye landmarks
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
        """
        Checks head position using the nose tip (landmark 1).
        Flags behavior if the nose deviates too far from center.
        """
        nose = landmarks[1]

        if abs(nose.x - 0.5) > self.center_tolerance:
            if nose.x < 0.5:
                self.current_status = "Brief: Head Rotated Left"
            else:
                self.current_status = "Brief: Head Rotated Right"
            return False

        if nose.y < 0.4:
            self.current_status = "Brief: Head Moved Up"
            return False
        elif nose.y > 0.6:
            self.current_status = "Fully Acceptable: Head Moved Down"
            return True

        self.current_status = "Normal Behavior"
        return True