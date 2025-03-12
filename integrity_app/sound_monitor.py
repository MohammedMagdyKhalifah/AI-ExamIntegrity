import speech_recognition as sr
import subprocess
from io import BytesIO


class SoundMonitor:
    def __init__(self, languages=None):
        """
        :param languages: معجم اللغات المطلوب التعرف عليها مع رموزها؛
                         الافتراضي: {"English": "en", "Arabic": "ar"}
        """
        self.recognizer = sr.Recognizer()
        self.languages = languages if languages is not None else {"English": "en", "Arabic": "ar"}
        # قائمة للكلمات أو العبارات المشتبه بها
        self.suspicious_words = [
            "غش", "مساعدة", "ساعدني", "حل", "cheat", "cheating", "help", "answers",
            "google", "copy", "الاجابه", "الاجابة", "اختار الاجابة", "الاختيار", "اختار",
            "answer", "حلها", "سؤال", "السؤال", "شابتر", "الشابتر", "chapter"
        ]

    def convert_webm_to_wav(self, audio_bytes):
        """
        يقوم بتحويل بيانات الصوت من صيغة WebM إلى WAV باستخدام ffmpeg عبر subprocess.

        :param audio_bytes: البيانات الخام للصوت بصيغة WebM.
        :return: بيانات الصوت المحولة إلى WAV كـ bytes أو None في حالة الفشل.
        """
        try:
            # استدعاء ffmpeg لتحويل من pipe:0 إلى WAV في pipe:1
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", "pipe:0", "-f", "wav", "pipe:1"],
                input=audio_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return result.stdout
        except Exception as e:
            print(f"Error converting webm to WAV via subprocess: {e}")
            return None

    def process_audio_chunk(self, audio_bytes, sample_rate=16000, sample_width=2):
        """
        يقوم بتحويل بيانات الصوت من WebM إلى WAV باستخدام ffmpeg،
        ثم يستخدم مكتبة SpeechRecognition للتعرف على الكلام بعدة لغات.

        :param audio_bytes: البيانات الخام للصوت (WebM) بالبايت.
        :param sample_rate: معدل العينة (افتراضي 16000).
        :param sample_width: بايت لكل عينة (افتراضي 2 لعينة 16-بت).
        :return: قاموس يحتوي على:
                 {
                     "recognized_texts": { "English": "...", "Arabic": "..." },
                     "violation_found": bool
                 }
        """
        wav_bytes = self.convert_webm_to_wav(audio_bytes)
        if wav_bytes is None:
            # استخدام البيانات الأصلية كخيار احتياطي (قد لا يكون صالحاً)
            wav_bytes = audio_bytes

        recognized_texts = {}
        violation_found = False

        try:
            audio_data = sr.AudioData(wav_bytes, sample_rate, sample_width)
        except Exception as e:
            print(f"Error creating AudioData: {e}")
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
                if lang == "English":
                    text = "No speech recognized"
                elif lang == "Arabic":
                    text = "لم يتم التعرف على الكلام"
            recognized_texts[lang] = text

            for suspicious_word in self.suspicious_words:
                if suspicious_word.lower() in text.lower():
                    violation_found = True

        return {
            "recognized_texts": recognized_texts,
            "violation_found": violation_found
        }