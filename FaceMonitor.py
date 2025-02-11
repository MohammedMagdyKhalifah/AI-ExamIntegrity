import cv2
import mediapipe as mp
import time

class FaceMonitor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # تفعيل refine_landmarks لمزيد من الدقة
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        self.mp_drawing = mp.solutions.drawing_utils

        self.suspicious_threshold = 1.5  # مدة السماح بالسلوك الطبيعي (1.5 ثانية)
        self.center_tolerance = 0.30     # نسبة انحراف مقبولة من المركز (30%)

        self.start_time = time.time()
        self.suspicious_flag = False
        self.behavior_description = "Normal Behavior"

    def detect_eye_gaze(self, landmarks):
        """
        الكشف عن اتجاه النظر باستخدام معالم العين.
        تُحسب النقطة المتوسطة للعينين الخارجية (landmarks 33 و263)
        ثم يتم التحقق من انحرافها عن المركز (0.5).
        كما يتم مقارنة معالم العين الداخلية (133 و362) لمحاولة تحديد النظر للأعلى/للأسفل.
        """
        left_eye_outer = landmarks[33]
        right_eye_outer = landmarks[263]
        left_eye_inner = landmarks[133]
        right_eye_inner = landmarks[362]

        # حساب النقطة المتوسطة للعينين الخارجية
        mid_point_x = (left_eye_outer.x + right_eye_outer.x) / 2
        deviation_from_center = abs(mid_point_x - 0.5)

        if deviation_from_center > self.center_tolerance:
            if mid_point_x < 0.5:
                self.behavior_description = "Brief: Looking Left"
            else:
                self.behavior_description = "Brief: Looking Right"
            return False  # لا ينظر مباشرة إلى الشاشة
        else:
            # التحقق من الاتجاه العمودي باستخدام العين الداخلية
            eye_vertical_diff = (left_eye_inner.y + right_eye_inner.y) / 2
            center_y = 0.5

            if eye_vertical_diff < center_y - 0.15:
                self.behavior_description = "Brief: Looking Up"
                return False
            elif eye_vertical_diff > center_y + 0.10:
                self.behavior_description = "Fully Acceptable: Looking Down"
                return True
            else:
                self.behavior_description = "Normal Behavior"
                return True

    def detect_head_movement(self, landmarks):
        """
        الكشف عن حركة الرأس باستخدام موقع طرف الأنف (landmark 1).
        إذا خرج موقع الأنف (أو تغير موضعه رأسيًا بشكل غير مقبول) عن النطاق المركزي،
        يعتبر السلوك مشبوهًا.
        في هذا التعديل:
         - تحرك الرأس للأسفل (nose_tip.y > 0.6) يكون مقبولاً.
         - تحرك الرأس للأعلى (nose_tip.y < 0.4) أو إلى الجوانب (انحراف x > center_tolerance) غير مقبول.
        """
        nose_tip = landmarks[1]  # معلم طرف الأنف

        # التحقق من الانحراف الأفقي للأنف عن المركز
        if abs(nose_tip.x - 0.5) > self.center_tolerance:
            if nose_tip.x < 0.5:
                self.behavior_description = "Brief: Head Rotated Left"
            else:
                self.behavior_description = "Brief: Head Rotated Right"
            return False

        # التحقق من الانحراف العمودي للأنف:
        if nose_tip.y < 0.4:
            self.behavior_description = "Brief: Head Moved Up"
            return False
        elif nose_tip.y > 0.6:
            self.behavior_description = "Fully Acceptable: Head Moved Down"
            return True

        self.behavior_description = "Normal Behavior"
        return True

    def detect_suspicious_behavior(self, image, landmarks):
        """
        يجمع بين الكشف عن اتجاه النظر وحركة الرأس.
        إذا كان أحدهما يشير إلى سلوك غير طبيعي (أي أن العين أو الأنف لا في الموضع المقبول)، يبدأ العداد.
        إذا استمر السلوك لأكثر من الفترة المسموحة (suspicious_threshold)، يتم عرض الإنذار.
        """
        is_eye_on_screen = self.detect_eye_gaze(landmarks)
        is_head_centered = self.detect_head_movement(landmarks)

        if not is_eye_on_screen or not is_head_centered:
            if not self.suspicious_flag:
                self.start_time = time.time()
                self.suspicious_flag = True
            elif time.time() - self.start_time > self.suspicious_threshold:
                cv2.putText(image, f"Suspicious: {self.behavior_description}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            self.suspicious_flag = False

        cv2.putText(image, self.behavior_description, (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return image

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks,
                    self.mp_face_mesh.FACEMESH_TESSELATION)
                frame = self.detect_suspicious_behavior(frame, face_landmarks.landmark)

        return frame

def main():
    cap = cv2.VideoCapture(0)
    face_monitor = FaceMonitor()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = face_monitor.process_frame(frame)
        cv2.imshow('Suspicious Behavior Detection', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()