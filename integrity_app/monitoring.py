import cv2
import time
import numpy as np
import mediapipe as mp


class FaceMonitor:
    def __init__(self):
        self.face_mesh_module = mp.solutions.face_mesh
        # Initialize face mesh with refined landmarks (which include iris info).
        self.face_mesh = self.face_mesh_module.FaceMesh(refine_landmarks=True)
        self.drawing_utils = mp.solutions.drawing_utils

        # Parameters
        self.suspicious_threshold = 1.5  # seconds before alerting
        self.center_tolerance = 0.10  # fallback if iris not available

        self.last_normal_time = time.time()
        self.suspicious_active = False
        self.current_status = "Normal Behavior"

    # Helper: extract point as tuple
    def _point(self, p):
        return (p.x, p.y)

    # Helper: Euclidean distance between two points (tuples)
    def _dist(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

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
            drawing_spec = self.drawing_utils.DrawingSpec(color=(245, 245, 245), thickness=1, circle_radius=1)
            for face_landmarks in results.multi_face_landmarks:
                self.drawing_utils.draw_landmarks(
                    frame, face_landmarks, self.face_mesh_module.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec
                )
                self._draw_eye_points(frame, face_landmarks.landmark)
                frame = self.detect_violation(frame, face_landmarks.landmark)
        return frame

    def _draw_eye_points(self, frame, landmarks):
        height, width, _ = frame.shape

        # Left eye boundaries.
        left_outer = landmarks[33]
        left_inner = landmarks[133]
        left_top = landmarks[159]
        left_bottom = landmarks[145]
        # Draw left eye keypoints.
        cv2.circle(frame, (int(left_outer.x * width), int(left_outer.y * height)), 2, (0, 0, 255), -1)  # Red
        cv2.circle(frame, (int(left_inner.x * width), int(left_inner.y * height)), 2, (0, 255, 0), -1)  # Green
        cv2.circle(frame, (int(left_top.x * width), int(left_top.y * height)), 2, (255, 0, 255), -1)  # Magenta
        cv2.circle(frame, (int(left_bottom.x * width), int(left_bottom.y * height)), 2, (255, 255, 0), -1)  # Cyan

        # Left iris.
        left_iris_points = landmarks[473:478]
        left_iris_center_x = sum(p.x for p in left_iris_points) / len(left_iris_points)
        left_iris_center_y = sum(p.y for p in left_iris_points) / len(left_iris_points)
        cv2.circle(frame, (int(left_iris_center_x * width), int(left_iris_center_y * height)), 2, (255, 0, 0),
                   -1)  # Blue

        # Right eye boundaries.
        right_outer = landmarks[263]
        right_inner = landmarks[362]
        right_top = landmarks[386]
        right_bottom = landmarks[374]
        cv2.circle(frame, (int(right_outer.x * width), int(right_outer.y * height)), 2, (255, 0, 255), -1)  # Magenta
        cv2.circle(frame, (int(right_inner.x * width), int(right_inner.y * height)), 2, (0, 255, 255), -1)  # Yellow
        cv2.circle(frame, (int(right_top.x * width), int(right_top.y * height)), 2, (0, 128, 255), -1)  # Orange-ish
        cv2.circle(frame, (int(right_bottom.x * width), int(right_bottom.y * height)), 2, (255, 128, 0),
                   -1)  # Light Blue

        # Right iris.
        right_iris_points = landmarks[468:473]
        right_iris_center_x = sum(p.x for p in right_iris_points) / len(right_iris_points)
        right_iris_center_y = sum(p.y for p in right_iris_points) / len(right_iris_points)
        cv2.circle(frame, (int(right_iris_center_x * width), int(right_iris_center_y * height)), 2, (100, 100, 255),
                   -1)  # Light Purple

    def _check_eye_gaze(self, landmarks):
        # Use this method if we have refined landmarks (>=478).
        if len(landmarks) >= 478:
            # --- LEFT EYE ---
            left_boundaries = [landmarks[33], landmarks[133], landmarks[159], landmarks[145]]
            # Compute the center of the left eye (average of four boundary points).
            left_center = (
                sum(p.x for p in left_boundaries) / 4.0,
                sum(p.y for p in left_boundaries) / 4.0
            )
            # Compute the iris center.
            left_iris_points = landmarks[473:478]
            left_iris_center = (
                sum(p.x for p in left_iris_points) / len(left_iris_points),
                sum(p.y for p in left_iris_points) / len(left_iris_points)
            )
            suspicious_conditions = []
            # For each boundary of the left eye, check the ratio of
            # distance(iris, boundary) / distance(eye_center, boundary)
            left_labels = ["Outer", "Inner", "Top", "Bottom"]
            for boundary, label in zip(left_boundaries, left_labels):
                eye_boundary = self._point(boundary)
                d_baseline = self._dist(left_center, eye_boundary)
                d_iris = self._dist(left_iris_center, eye_boundary)
                # If the iris is within 10% of the distance from the eye center to the boundary:
                if d_baseline > 0 and d_iris < 0.1 * d_baseline:
                    suspicious_conditions.append(f"Left {label}")

            # --- RIGHT EYE ---
            right_boundaries = [landmarks[263], landmarks[362], landmarks[386], landmarks[374]]
            right_center = (
                sum(p.x for p in right_boundaries) / 4.0,
                sum(p.y for p in right_boundaries) / 4.0
            )
            right_iris_points = landmarks[468:473]
            right_iris_center = (
                sum(p.x for p in right_iris_points) / len(right_iris_points),
                sum(p.y for p in right_iris_points) / len(right_iris_points)
            )
            right_labels = ["Outer", "Inner", "Top", "Bottom"]
            for boundary, label in zip(right_boundaries, right_labels):
                eye_boundary = self._point(boundary)
                d_baseline = self._dist(right_center, eye_boundary)
                d_iris = self._dist(right_iris_center, eye_boundary)
                if d_baseline > 0 and d_iris < 0.1 * d_baseline:
                    suspicious_conditions.append(f"Right {label}")

            if suspicious_conditions:
                self.current_status = "Suspicious: " + ", ".join(suspicious_conditions)
                return False
            else:
                self.current_status = "Normal Behavior"
                return True
        else:
            # Fallback: simple checks (not using iris)
            left_eye_outer = landmarks[33]
            right_eye_outer = landmarks[263]
            mid_x = (left_eye_outer.x + right_eye_outer.x) / 2
            horizontal_deviation = abs(mid_x - 0.5)
            if horizontal_deviation > self.center_tolerance:
                self.current_status = "Brief: Looking Left" if mid_x < 0.5 else "Brief: Looking Right"
                return False
            else:
                avg_y = (landmarks[133].y + landmarks[362].y) / 2
                center_y = 0.5
                if avg_y < center_y - 0.15:
                    self.current_status = "Brief: Looking Up"
                    return False
                elif avg_y > center_y + 0.10:
                    self.current_status = "Brief: Looking Down"
                    return False
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
            "is_suspicious": self.suspicious_active and (
                        time.time() - self.last_normal_time > self.suspicious_threshold),
            "frame_data": processed_bytes
        }