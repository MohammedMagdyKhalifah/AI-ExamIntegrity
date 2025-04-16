import cv2
import time
import numpy as np
import mediapipe as mp


class FaceMonitor:
    def __init__(self,
                 sunglasses_detection_threshold=50,  # Minimum confidence (%) to flag sunglasses.
                 object_detection_threshold=40  # Minimum confidence (%) to flag a cheating object.
                 ):
        # Initialize MediaPipe's face mesh with refined landmarks.
        self.face_mesh_module = mp.solutions.face_mesh
        self.face_mesh = self.face_mesh_module.FaceMesh(refine_landmarks=True)
        self.drawing_utils = mp.solutions.drawing_utils

        # Standard configuration thresholds.
        self.suspicious_threshold = 1.5  # seconds before alerting.
        self.center_tolerance = 0.10  # acceptable deviation from center (fallback).

        # Sensitivity parameters for external classifiers.
        self.sunglasses_detection_threshold = sunglasses_detection_threshold
        self.object_detection_threshold = object_detection_threshold

        # Timing and status tracking.
        self.last_normal_time = time.time()
        self.suspicious_active = False
        self.current_status = "Normal Behavior"

        # These attributes will store separate external detection results.
        self.sunglasses_detection = {"detected": False, "confidence": 0}
        self.object_detection = {"detected": False, "confidence": 0}

    # ---------------- Helper Functions ----------------
    def _point(self, p):
        return (p.x, p.y)

    def _dist(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    # ---------------- Simulated External Detection ----------------
    def classify_sunglasses(self, frame):
        """
        Simulates a MediaPipe image classification model for sunglasses detection.
        Returns a confidence percentage (0-100). Replace with your actual classifier.
        """
        simulated_confidence = 68.0  # Example simulated value.
        return simulated_confidence

    def detect_cheating_objects_classification(self, frame):
        """
        Simulates a MediaPipe object detection model for cheating items (e.g. phone, book, remote).
        Returns a confidence percentage (0-100). Replace with your actual object detector.
        """
        simulated_confidence = 45.0  # Example simulated value.
        return simulated_confidence

    def _draw_sunglasses_box(self, frame, landmarks, width, height):
        """
        Draws green rectangles around both eye regions using specified landmarks.
        """
        # Left eye: landmarks 33, 133, 159, 145.
        left_points = [landmarks[33], landmarks[133], landmarks[159], landmarks[145]]
        left_coords = [(int(p.x * width), int(p.y * height)) for p in left_points]
        x_min_left = min(pt[0] for pt in left_coords)
        y_min_left = min(pt[1] for pt in left_coords)
        x_max_left = max(pt[0] for pt in left_coords)
        y_max_left = max(pt[1] for pt in left_coords)
        cv2.rectangle(frame, (x_min_left, y_min_left), (x_max_left, y_max_left), (0, 255, 0), 2)

        # Right eye: landmarks 362, 263, 386, 374.
        right_points = [landmarks[362], landmarks[263], landmarks[386], landmarks[374]]
        right_coords = [(int(p.x * width), int(p.y * height)) for p in right_points]
        x_min_right = min(pt[0] for pt in right_coords)
        y_min_right = min(pt[1] for pt in right_coords)
        x_max_right = max(pt[0] for pt in right_coords)
        y_max_right = max(pt[1] for pt in right_coords)
        cv2.rectangle(frame, (x_min_right, y_min_right), (x_max_right, y_max_right), (0, 255, 0), 2)

    def _draw_cheating_object_box(self, frame):
        """
        Draws a red rectangle over the lower 30% of the frame – the region where a phone, book, or remote might be.
        """
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, int(0.7 * h)), (w, h), (0, 0, 255), 2)

    # ---------------- Core Analysis Methods ----------------
    def track_gaze(self, landmarks):
        """
        Evaluates eye gaze and head movement.
        Returns True only if both are acceptable.
        """
        eyes_ok = self._check_eye_gaze(landmarks)
        head_ok = self._check_head_movement(landmarks)
        return eyes_ok and head_ok

    def detect_violation(self, frame, landmarks):
        """
        Combines the results of gaze/head analysis with external detection results for sunglasses and objects.
        Builds a status string that includes the detection confidence percentages.
        """
        is_normal = self.track_gaze(landmarks)

        # Run external classifiers on the full frame.
        sunglasses_confidence = self.classify_sunglasses(frame)
        object_confidence = self.detect_cheating_objects_classification(frame)

        # Save the external results in separate variables.
        self.sunglasses_detection = {
            "detected": sunglasses_confidence >= self.sunglasses_detection_threshold,
            "confidence": sunglasses_confidence
        }
        self.object_detection = {
            "detected": object_confidence >= self.object_detection_threshold,
            "confidence": object_confidence
        }

        status_list = []
        if self.sunglasses_detection["detected"]:
            status_list.append(f"Sunglasses: {self.sunglasses_detection['confidence']:.0f}%")
        if self.object_detection["detected"]:
            status_list.append(f"Object: {self.object_detection['confidence']:.0f}%")
        if not is_normal:
            status_list.append(self.current_status)

        if status_list:
            self.current_status = "Suspicious: " + ", ".join(status_list)
        else:
            self.current_status = "Normal Behavior"

        # Draw external detection indicators on the frame regardless of face detection.
        height, width, _ = frame.shape
        if self.sunglasses_detection["detected"]:
            # Attempt to draw sunglasses boxes if face landmarks are available.
            # (If face landmarks are not available, the classifier result is still used in the status.)
            try:
                self._draw_sunglasses_box(frame, landmarks, width, height)
            except Exception:
                pass
        if self.object_detection["detected"]:
            self._draw_cheating_object_box(frame)

        # Update suspicious activity based on timing.
        if self.current_status.startswith("Suspicious") and not self.suspicious_active:
            self.last_normal_time = time.time()
            self.suspicious_active = True
        elif self.suspicious_active and (time.time() - self.last_normal_time > self.suspicious_threshold):
            self.annotate_alert(frame, self.current_status)
        else:
            self.suspicious_active = False

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
        Always runs external detection on the full frame (for sunglasses and objects),
        then attempts to detect and analyze the face using MediaPipe's face mesh.
        If no face is detected, a "No face detected" label is added.
        """
        # Always run external detectors on the full frame.
        # Run object detection classification.
        object_confidence = self.detect_cheating_objects_classification(frame)
        if object_confidence >= self.object_detection_threshold:
            self._draw_cheating_object_box(frame)

        # Run sunglasses classification.
        sunglasses_confidence = self.classify_sunglasses(frame)
        # Note: for drawing the sunglasses box, we need face landmarks.
        # That will be handled later if a face is detected.

        # Always attempt face analysis.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            drawing_spec = self.drawing_utils.DrawingSpec(color=(245, 245, 245), thickness=1, circle_radius=1)
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                self.drawing_utils.draw_landmarks(
                    frame,
                    face_landmarks,
                    self.face_mesh_module.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec
                )
                self._draw_eye_points(frame, landmarks)
                frame = self.detect_violation(frame, landmarks)
                # If sunglasses are detected externally, draw the box using face landmarks.
                if sunglasses_confidence >= self.sunglasses_detection_threshold:
                    self._draw_sunglasses_box(frame, landmarks, frame.shape[1], frame.shape[0])
        else:
            cv2.putText(frame, "No face detected", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return frame

    def _draw_eye_points(self, frame, landmarks):
        """
        Draws key eye landmarks and bounding rectangles ("squares") around the eyes.
        """
        height, width, _ = frame.shape

        # --- LEFT EYE (landmarks 33, 133, 159, 145) ---
        left_points = [landmarks[33], landmarks[133], landmarks[159], landmarks[145]]
        left_coords = [(int(p.x * width), int(p.y * height)) for p in left_points]
        cv2.circle(frame, left_coords[0], 2, (0, 0, 255), -1)  # Red (Outer)
        cv2.circle(frame, left_coords[1], 2, (0, 255, 0), -1)  # Green (Inner)
        cv2.circle(frame, left_coords[2], 2, (255, 0, 255), -1)  # Magenta (Top)
        cv2.circle(frame, left_coords[3], 2, (255, 255, 0), -1)  # Cyan (Bottom)
        x_min_left = min(pt[0] for pt in left_coords)
        x_max_left = max(pt[0] for pt in left_coords)
        y_min_left = min(pt[1] for pt in left_coords)
        y_max_left = max(pt[1] for pt in left_coords)
        cv2.rectangle(frame, (x_min_left, y_min_left), (x_max_left, y_max_left), (200, 200, 200), 1)
        left_iris_points = landmarks[473:478]
        left_iris_center = (int(sum(p.x for p in left_iris_points) / len(left_iris_points) * width),
                            int(sum(p.y for p in left_iris_points) / len(left_iris_points) * height))
        cv2.circle(frame, left_iris_center, 2, (255, 0, 0), -1)  # Blue

        # --- RIGHT EYE (landmarks 362, 263, 386, 374) ---
        right_points = [landmarks[362], landmarks[263], landmarks[386], landmarks[374]]
        right_coords = [(int(p.x * width), int(p.y * height)) for p in right_points]
        cv2.circle(frame, right_coords[0], 2, (0, 255, 255), -1)  # Yellow (Inner)
        cv2.circle(frame, right_coords[1], 2, (255, 0, 255), -1)  # Magenta (Outer)
        cv2.circle(frame, right_coords[2], 2, (0, 128, 255), -1)  # Orange-ish (Top)
        cv2.circle(frame, right_coords[3], 2, (255, 128, 0), -1)  # Light Blue (Bottom)
        x_min_right = min(pt[0] for pt in right_coords)
        x_max_right = max(pt[0] for pt in right_coords)
        y_min_right = min(pt[1] for pt in right_coords)
        y_max_right = max(pt[1] for pt in right_coords)
        cv2.rectangle(frame, (x_min_right, y_min_right), (x_max_right, y_max_right), (200, 200, 200), 1)
        right_iris_points = landmarks[468:473]
        right_iris_center = (int(sum(p.x for p in right_iris_points) / len(right_iris_points) * width),
                             int(sum(p.y for p in right_iris_points) / len(right_iris_points) * height))
        cv2.circle(frame, right_iris_center, 2, (100, 100, 255), -1)  # Light Purple

    def _check_eye_gaze(self, landmarks):
        """
        Uses the horizontal positions of the iris centers (derived from the face mesh landmarks)
        relative to the eye boxes to flag suspicious gaze. (Vertical evaluation is not performed here.)
        """
        if len(landmarks) >= 478:
            suspicious_conditions = []

            # --- LEFT EYE ---
            left_boundaries = {"Outer": landmarks[33], "Inner": landmarks[133]}
            left_x_min = min(left_boundaries["Outer"].x, left_boundaries["Inner"].x)
            left_x_max = max(left_boundaries["Outer"].x, left_boundaries["Inner"].x)
            left_iris_points = landmarks[473:478]
            left_iris_center = (sum(p.x for p in left_iris_points) / len(left_iris_points),
                                sum(p.y for p in left_iris_points) / len(left_iris_points))
            norm_left_x = (left_iris_center[0] - left_x_min) / (left_x_max - left_x_min) if (
                        left_x_max - left_x_min) else 0.5

            # --- RIGHT EYE ---
            right_boundaries = {"Inner": landmarks[362], "Outer": landmarks[263]}
            right_x_min = min(right_boundaries["Inner"].x, right_boundaries["Outer"].x)
            right_x_max = max(right_boundaries["Inner"].x, right_boundaries["Outer"].x)
            right_iris_points = landmarks[468:473]
            right_iris_center = (sum(p.x for p in right_iris_points) / len(right_iris_points),
                                 sum(p.y for p in right_iris_points) / len(right_iris_points))
            norm_right_x = (right_iris_center[0] - right_x_min) / (right_x_max - right_x_min) if (
                        right_x_max - right_x_min) else 0.5

            # Check horizontal proximity: flag if iris center is very near the extreme edges (<0.10 or >0.90).
            if norm_left_x < 0.10:
                suspicious_conditions.append("Left Outer")
            if norm_left_x > 0.90:
                suspicious_conditions.append("Left Inner")
            if norm_right_x < 0.10:
                suspicious_conditions.append("Right Inner")
            if norm_right_x > 0.90:
                suspicious_conditions.append("Right Outer")

            if suspicious_conditions:
                self.current_status = "Suspicious: " + ", ".join(suspicious_conditions)
                return False
            else:
                self.current_status = "Normal Behavior"
                return True
        else:
            # Fallback: simple horizontal check.
            left_eye_outer = landmarks[33]
            right_eye_outer = landmarks[263]
            mid_x = (left_eye_outer.x + right_eye_outer.x) / 2
            if abs(mid_x - 0.5) > self.center_tolerance:
                self.current_status = "Brief: Looking Left" if mid_x < 0.5 else "Brief: Looking Right"
                return False
            else:
                self.current_status = "Normal Behavior"
                return True

    def _check_head_movement(self, landmarks):
        """
        Checks head position using the nose tip (landmark 1).
        """
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
        Processes a frame from byte data. Always runs external detection (sunglasses and object)
        on the full frame, then runs face detection/analysis if a face is present.
        Returns a dictionary with:
          - "status": overall status string,
          - "sunglasses_detection": dictionary with sunglasses detection result and confidence,
          - "object_detection": dictionary with object detection result and confidence,
          - "is_suspicious": a flag based on timing,
          - "frame_data": JPEG-encoded processed frame.
        """
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        height, width, _ = frame.shape

        # Always run external classifiers on the full frame.
        sunglasses_confidence = self.classify_sunglasses(frame)
        object_confidence = self.detect_cheating_objects_classification(frame)
        self.sunglasses_detection = {
            "detected": sunglasses_confidence >= self.sunglasses_detection_threshold,
            "confidence": sunglasses_confidence
        }
        self.object_detection = {
            "detected": object_confidence >= self.object_detection_threshold,
            "confidence": object_confidence
        }

        # Draw external detection indicators even if no face is detected.
        if self.object_detection["detected"]:
            self._draw_cheating_object_box(frame)
        # Note: For sunglasses, drawing the eye boxes requires face landmarks.

        # Run face mesh detection.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark
                if self.sunglasses_detection["detected"]:
                    self._draw_sunglasses_box(frame, landmarks, width, height)
                drawing_spec = self.drawing_utils.DrawingSpec(color=(245, 245, 245), thickness=1, circle_radius=1)
                self.drawing_utils.draw_landmarks(
                    frame, face_landmarks, self.face_mesh_module.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec, connection_drawing_spec=drawing_spec
                )
                self._draw_eye_points(frame, landmarks)
                frame = self.detect_violation(frame, landmarks)
        else:
            cv2.putText(frame, "No face detected", (50, 150), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)

        # Encode processed frame.
        retval, buffer = cv2.imencode('.jpg', frame)
        processed_bytes = buffer.tobytes()
        return {
            "status": self.current_status,
            "sunglasses_detection": self.sunglasses_detection,
            "object_detection": self.object_detection,
            "is_suspicious": self.suspicious_active and (
                        time.time() - self.last_normal_time > self.suspicious_threshold),
            "frame_data": processed_bytes
        }