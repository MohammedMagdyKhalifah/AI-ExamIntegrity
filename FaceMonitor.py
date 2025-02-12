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
        self.gazeStatus = "Normal Behavior"  # بدلًا من behavior_description

    def trackGaze(self, landmarks):
        """
        يجمع بين الكشف عن اتجاه النظر (العين) وحركة الرأس.
        إذا كانت العين أو الرأس خارج النطاق المقبول، يعيد False.
        بخلاف ذلك يعيد True.
        """
        eye_ok = self._detect_eye_gaze(landmarks)
        head_ok = self._detect_head_movement(landmarks)
        return eye_ok and head_ok

    def detectViolation(self, image, landmarks):
        """
        يتحقق مما إذا كان هناك سلوك مشبوه بناءً على trackGaze().
        إذا استمر السلوك لأكثر من suspicious_threshold، يتم استدعاء generateAlert().
        """
        is_gaze_ok = self.trackGaze(landmarks)
        if not is_gaze_ok:
            # إذا كانت هذه أول مرة نرصد سلوكًا مشبوهًا، نبدأ العداد
            if not self.suspicious_flag:
                self.start_time = time.time()
                self.suspicious_flag = True
            # إذا تجاوزنا مدة السماح، نعرض التنبيه
            elif time.time() - self.start_time > self.suspicious_threshold:
                self.generateAlert(image, f"Suspicious: {self.gazeStatus}")
        else:
            # إعادة الضبط إذا عاد السلوك للوضع الطبيعي
            self.suspicious_flag = False

        # في كل الأحوال نعرض الحالة الحالية (gazeStatus) على الشاشة
        cv2.putText(
            image, self.gazeStatus, (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )
        return image

    def generateAlert(self, image, message):
        """
        يعرض رسالة تنبيهية على إطار الفيديو عند اكتشاف سلوك مشبوه.
        """
        cv2.putText(
            image, message, (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )

    def analyzeFace(self, frame):
        """
        الدالة الأساسية لمعالجة الإطار (الصورة) الملتقطة من الكاميرا.
        تقوم باكتشاف الوجه ومعالمه، ثم تستدعي detectViolation للتحقق من أي مخالفة.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # رسم المعالم على الوجه
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks,
                    self.mp_face_mesh.FACEMESH_TESSELATION
                )
                # التحقق من وجود انتهاك
                frame = self.detectViolation(frame, face_landmarks.landmark)

        return frame

    # ----------------------------------------------------------------------------
    # الدوال المساعدة (خاصة) للكشف عن حركة العين والرأس
    # ----------------------------------------------------------------------------
    def _detect_eye_gaze(self, landmarks):
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

        # التحقق من الانحراف الأفقي
        if deviation_from_center > self.center_tolerance:
            if mid_point_x < 0.5:
                self.gazeStatus = "Brief: Looking Left"
            else:
                self.gazeStatus = "Brief: Looking Right"
            return False
        else:
            # التحقق من الاتجاه العمودي باستخدام العين الداخلية
            eye_vertical_diff = (left_eye_inner.y + right_eye_inner.y) / 2
            center_y = 0.5

            if eye_vertical_diff < center_y - 0.15:
                self.gazeStatus = "Brief: Looking Up"
                return False
            elif eye_vertical_diff > center_y + 0.10:
                self.gazeStatus = "Fully Acceptable: Looking Down"
                return True
            else:
                self.gazeStatus = "Normal Behavior"
                return True

    def _detect_head_movement(self, landmarks):
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
                self.gazeStatus = "Brief: Head Rotated Left"
            else:
                self.gazeStatus = "Brief: Head Rotated Right"
            return False

        # التحقق من الانحراف العمودي للأنف:
        if nose_tip.y < 0.4:
            self.gazeStatus = "Brief: Head Moved Up"
            return False
        elif nose_tip.y > 0.6:
            self.gazeStatus = "Fully Acceptable: Head Moved Down"
            return True

        self.gazeStatus = "Normal Behavior"
        return True

def main():
    cap = cv2.VideoCapture(0)
    face_monitor = FaceMonitor()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # استدعاء analyzeFace بدلاً من process_frame
        frame = face_monitor.analyzeFace(frame)
        cv2.imshow('Suspicious Behavior Detection', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()