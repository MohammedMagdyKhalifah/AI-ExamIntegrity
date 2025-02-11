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

        self.microphone = sr.Microphone()

    def adjust_for_ambient_noise(self):
        """
        يقوم بضبط حساسية الميكروفون حسب الضوضاء المحيطة.
        """
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Calibrated for ambient noise.")

    def listen(self):
        """
        الاستماع لمرة واحدة من الميكروفون باستخدام timeout و phrase_time_limit.
        :return: كائن الصوت (audio)
        """
        with self.microphone as source:
            print("Say something in English or Arabic...")
            audio = self.recognizer.listen(source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
        return audio

    def recognize(self, audio):
        """
        يحاول التعرف على الكلام في الصوت لكل لغة محددة.
        :param audio: كائن الصوت المُلتقط
        :return: معجم يحتوي على نتائج التعرف لكل لغة
        """
        results = {}
        for lang, code in self.languages.items():
            try:
                text = self.recognizer.recognize_google(audio, language=code)
                results[lang] = text
            except sr.UnknownValueError:
                # في حالة عدم فهم الصوت، نترك القيمة فارغة دون طباعة رسالة
                results[lang] = ""
            except sr.RequestError:
                # في حالة مشكلة في الاتصال، نقوم بطباعة رسالة ونترك النتيجة فارغة
                print(f"{lang}: Could not request results. Check your internet connection.")
                results[lang] = ""
        return results

    def run(self):
        """
        الحلقة الرئيسية للاستماع المستمر والتعرف على الكلام.
        """
        self.adjust_for_ambient_noise()
        print("Listening continuously. Press Ctrl+C to exit.")
        try:
            while True:
                audio = self.listen()
                results = self.recognize(audio)
                for lang, text in results.items():
                    if text:
                        print(f"{lang}: {text}")
                # يمكنك هنا إضافة أي منطق إضافي لمعالجة النتائج
        except KeyboardInterrupt:
            print("Exiting...")

if __name__ == "__main__":
    recognizer = SoundMonitor(timeout=3, phrase_time_limit=10, pause_threshold=1.2)
    recognizer.run()