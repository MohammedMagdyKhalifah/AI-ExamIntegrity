import speech_recognition as sr


class SoundMonitor:
    def __init__(self, timeout=3, phrase_time_limit=10, pause_threshold=1.2, languages=None):
        """
        :param timeout: مدة الانتظار (بالثواني) قبل بدء الكلام
        :param phrase_time_limit: أقصى مدة لتسجيل العبارة (بالثواني)
        :param pause_threshold: المدة الزمنية التي يعتبرها البرنامج نهاية العبارة بعد الصمت
        :param languages: معجم اللغات المطلوب التعرف عليها مع رموزها؛ الافتراضي: {"English": "en", "Arabic": "ar"}
        """
        self.recognizer = sr.Recognizer()
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

        # ضبط إعدادات التعرف
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.dynamic_energy_threshold = True

        # تعيين اللغات الافتراضية إذا لم تُحدد
        self.languages = languages if languages is not None else {"English": "en", "Arabic": "ar"}

        # الميكروفون
        self.microphone = sr.Microphone()

        # الخصائص بحسب الكلاس دايجرام
        self.ambientSoundData = None  # لتخزين بيانات الصوت الملتقطة
        self.detectedKeywords = {}  # لتخزين النصوص أو الكلمات المكتشفة (باللغة المفتاحية)

        # قائمة (مصفوفة) للكلمات أو العبارات التي تعتبر "مشتبه بها"
        self.suspicious_words = [
            "غش", "مساعدة", "ساعدني", "حل", "cheat", "cheating", "help", "answers",
            "google", "copy", "الاجابه", "الاجابة", "اختار الاجابة", "الاختيار", "اختار",
            "answer", "حلها", "سؤال", "السؤال", "شابتر", "الشابتر", "chapter"
        ]

        # قائمة لتخزين كل النصوص التي يتم التعرف عليها
        self.recognizedTexts = []

    def analyzeSoundData(self):
        """
        تقوم بضبط حساسية الميكروفون حسب الضوضاء المحيطة (تهيئة أولية).
        يمكن توسيع هذه الدالة لاحقًا لتحليل الصوت بطرق مختلفة.
        """
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Calibrated for ambient noise.")

    def detectViolation(self):
        """
        1) الاستماع للصوت من الميكروفون.
        2) التعرف على النص بأكثر من لغة (إنجليزي/عربي).
        3) تعيين القيم في الخصائص: ambientSoundData و detectedKeywords.
        4) فحص الكلمات المشتبه بها.
        """
        with self.microphone as source:
            print("Say something in English or Arabic...")
            try:
                audio = self.recognizer.listen(source,
                                               timeout=self.timeout,
                                               phrase_time_limit=self.phrase_time_limit)
            except sr.WaitTimeoutError:
                print("Timeout: لم يتم الكشف عن أي صوت خلال الفترة المحددة.")
                return False  # نعتبره عدم وجود مخالفة إذا لم يكن هناك صوت
        # حفظ الصوت الملتقط
        self.ambientSoundData = audio

        # محاولة التعرف على النص بجميع اللغات المحددة
        results = {}
        for lang, code in self.languages.items():
            try:
                text = self.recognizer.recognize_google(audio, language=code)
                results[lang] = text

                # طباعة النص الذي تم التعرف عليه
                print(f"[{lang}] Recognized text: {text}")

                # تخزين النص في القائمة الخاصة
                self.recognizedTexts.append(text)
            except sr.UnknownValueError:
                results[lang] = ""
            except sr.RequestError:
                print(f"{lang}: Could not request results. Check your internet connection.")
                results[lang] = ""

        # حفظ النصوص المكتشفة في الخاصية detectedKeywords (مقسمة حسب اللغة)
        self.detectedKeywords = results

        # منطق للكشف عن مخالفة (نبحث عن أي كلمة مشتبه بها داخل أي نص)
        violation_found = False
        for text in results.values():
            if not text.strip():
                continue
            for suspicious_word in self.suspicious_words:
                if suspicious_word.lower() in text.lower():
                    violation_found = True
                    break
            if violation_found:
                break

        return violation_found

    def generateAlert(self, violation):
        """
        في حال تم الكشف عن مخالفة (violation == True)، نقوم بإطلاق تنبيه.
        """
        if violation:
            print("حالة غش: تم رصد كلمات مشتبه بها!")
        else:
            print("No violation detected this time.")

    def run(self):
        """
        حلقة رئيسية للاستماع المستمر والتعرف على الكلام والكشف عن المخالفات.
        """
        # تهيئة الميكروفون/الصوت قبل البدء
        self.analyzeSoundData()
        print("Listening continuously. Press Ctrl+C to exit.")

        try:
            while True:
                # اكتشاف إن كان هناك مخالفة
                found_violation = self.detectViolation()
                # إصدار التنبيه بناءً على نتيجة الكشف
                self.generateAlert(found_violation)
        except KeyboardInterrupt:
            print("Exiting...")


if __name__ == "__main__":
    recognizer = SoundMonitor(timeout=3, phrase_time_limit=10, pause_threshold=1.2)
    recognizer.run()