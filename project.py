import cv2
import mediapipe as mp
import time
import math


class SuspiciousBehaviorDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        self.mp_drawing = mp.solutions.drawing_utils
        self.screen_width = 1280  # Set default screen width (can be calibrated)
        self.screen_height = 720  # Set default screen height (can be calibrated)
        self.suspicious_threshold = 1.5  # Allow natural behavior for 1.5 seconds
        self.center_tolerance = 0.30  # Allow 30% deviation from the center
        self.start_time = time.time()
        self.suspicious_flag = False
        self.behavior_description = "Normal Behavior"

    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def detect_eye_gaze(self, landmarks, image_shape):
        # Get landmarks for both eyes
        left_eye_outer = landmarks[33]
        right_eye_outer = landmarks[263]
        left_eye_inner = landmarks[133]
        right_eye_inner = landmarks[362]

        # Calculate the midpoint between the outer eye corners (rough head center)
        mid_point_x = (left_eye_outer.x + right_eye_outer.x) / 2

        # If the midpoint between the outer eyes deviates by 30% from the center, we flag a suspicious movement.
        deviation_from_center = abs(mid_point_x - 0.5)  # Deviation from center (0.5 represents the center)

        # Detect eye gaze direction
        if deviation_from_center > self.center_tolerance:  # Greater than 30% deviation from center
            if mid_point_x < 0.5:  # Looking left
                self.behavior_description = "Brief: Looking Left"
            else:  # Looking right
                self.behavior_description = "Brief: Looking Right"
            return False  # Not looking at the screen
        else:
            # We now check if the user is looking up or down based on eye inner landmarks
            eye_vertical_diff = (left_eye_inner.y + right_eye_inner.y) / 2  # Midpoint of inner eye Y-coordinate
            center_y = 0.5  # Assuming 0.5 is center for normalized values

            if eye_vertical_diff < center_y - 0.15:  # Looking up (using a 15% tolerance for looking up)
                self.behavior_description = "Brief: Looking Up"
                return False
            elif eye_vertical_diff > center_y + 0.10:  # Looking down (fully acceptable)
                self.behavior_description = "Fully Acceptable: Looking Down"
                return True  # Looking down is acceptable
            else:
                self.behavior_description = "Normal Behavior"
                return True  # Looking at the screen

    def detect_head_movement(self, landmarks):
        nose_tip = landmarks[1]  # Nose tip landmark
        left_cheek = landmarks[234]  # Left cheek
        right_cheek = landmarks[454]  # Right cheek

        # Calculate the distances to detect head rotation/tilting
        nose_center_distance = abs(nose_tip.x - 0.5)

        # Allow 30% tolerance for head movements left or right
        if nose_center_distance > self.center_tolerance:
            if nose_tip.x < 0.5:  # Head turned left
                self.behavior_description = "Brief: Head Moved Left"
            else:  # Head turned right
                self.behavior_description = "Brief: Head Moved Right"
            return False  # Head moved too far
        elif nose_tip.y < 0.4:  # Head tilted up
            self.behavior_description = "Brief: Head Moved Up"
            return False
        elif nose_tip.y > 0.6:  # Head tilted down (fully acceptable)
            self.behavior_description = "Fully Acceptable: Head Moved Down"
            return True  # Head down is acceptable
        else:
            self.behavior_description = "Normal Behavior"  # Head straight
            return True  # Natural movement

    def detect_suspicious_behavior(self, image, landmarks):
        image_height, image_width, _ = image.shape
        is_eye_on_screen = self.detect_eye_gaze(landmarks, image.shape)
        is_head_straight = self.detect_head_movement(landmarks)

        if not is_eye_on_screen or not is_head_straight:
            # Start a timer when suspicious behavior is detected
            if not self.suspicious_flag:
                self.start_time = time.time()
                self.suspicious_flag = True
            elif time.time() - self.start_time > self.suspicious_threshold:
                cv2.putText(image, f"Suspicious: {self.behavior_description}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            self.suspicious_flag = False  # Reset flag if behavior is normal

        # Always show the behavior description in normal conditions
        cv2.putText(image, self.behavior_description, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return image

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw face landmarks for visualization
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks,
                    self.mp_face_mesh.FACEMESH_TESSELATION)  # Use FACEMESH_TESSELATION for drawing

                # Detect suspicious behavior
                frame = self.detect_suspicious_behavior(frame, face_landmarks.landmark)

        return frame


def main():
    cap = cv2.VideoCapture(0)
    detector = SuspiciousBehaviorDetector()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Process the frame for suspicious behavior detection
        frame = detector.process_frame(frame)

        # Display the frame
        cv2.imshow('Suspicious Behavior Detection', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
