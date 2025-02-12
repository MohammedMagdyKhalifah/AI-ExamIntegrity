import unittest
from unittest.mock import MagicMock, patch
import speech_recognition as sr
from SoundMonitor import SoundMonitor


class TestSoundMonitor(unittest.TestCase):

    def setUp(self):
        """تهيئة كائن SoundMonitor مع استبدال الميكروفون بـ MagicMock."""
        self.sound_monitor = SoundMonitor(timeout=3, phrase_time_limit=10, pause_threshold=1.2)
        self.sound_monitor.microphone = MagicMock()

    # ========== 1) اختبار التهيئة ==========

    def test_constructor_default_languages(self):
        """تأكد من تعيين اللغات الافتراضية عند عدم تمريرها."""
        sm = SoundMonitor()
        self.assertEqual(sm.languages, {"English": "en", "Arabic": "ar"},
                         "يجب تعيين اللغات الافتراضية إن لم تُحدد.")

    def test_constructor_custom_languages(self):
        """تأكد من استخدام اللغات المخصصة إن تم تمريرها."""
        custom_langs = {"English": "en-US", "French": "fr-FR"}
        sm = SoundMonitor(languages=custom_langs)
        self.assertEqual(sm.languages, custom_langs,
                         "يجب استخدام اللغات المخصصة إن تم تمريرها.")

    # ========== 2) اختبار دالة analyzeSoundData ==========

    @patch.object(sr.Recognizer, 'adjust_for_ambient_noise')
    def test_analyzeSoundData(self, mock_adjust):
        """التأكد من استدعاء adjust_for_ambient_noise."""
        self.sound_monitor.analyzeSoundData()
        mock_adjust.assert_called_once()

    # ========== 3) اختبار detectViolation في سيناريوهات أساسية ==========

    @patch.object(sr.Recognizer, 'listen')
    def test_detectViolation_no_audio_timeout(self, mock_listen):
        """محاكاة عدم وجود صوت (WaitTimeoutError)."""
        mock_listen.side_effect = sr.WaitTimeoutError
        violation = self.sound_monitor.detectViolation()
        self.assertFalse(violation, "عند عدم وجود صوت، لا مخالفة.")

    @patch.object(sr.Recognizer, 'listen')
    @patch.object(sr.Recognizer, 'recognize_google')
    def test_detectViolation_unknown_value_error(self, mock_recognize, mock_listen):
        """محاكاة عدم فهم الكلام (UnknownValueError)."""
        mock_listen.return_value = MagicMock()
        mock_recognize.side_effect = sr.UnknownValueError
        violation = self.sound_monitor.detectViolation()
        self.assertFalse(violation)
        # تأكد أن كل لغة تم تخزينها كنص فارغ
        for text in self.sound_monitor.detectedKeywords.values():
            self.assertEqual(text, "")

    @patch.object(sr.Recognizer, 'listen')
    @patch.object(sr.Recognizer, 'recognize_google')
    def test_detectViolation_request_error(self, mock_recognize, mock_listen):
        """محاكاة خطأ في الطلب (RequestError)."""
        mock_listen.return_value = MagicMock()
        mock_recognize.side_effect = sr.RequestError("Network error")
        violation = self.sound_monitor.detectViolation()
        self.assertFalse(violation)
        for text in self.sound_monitor.detectedKeywords.values():
            self.assertEqual(text, "")

    @patch.object(sr.Recognizer, 'listen')
    @patch.object(sr.Recognizer, 'recognize_google')
    def test_detectViolation_no_violation(self, mock_recognize, mock_listen):
        """نص سليم لا يحتوي أي كلمة مشتبه بها -> لا يوجد مخالفة."""
        mock_listen.return_value = MagicMock()
        mock_recognize.return_value = "Hello world"

        violation = self.sound_monitor.detectViolation()
        self.assertFalse(violation)
        self.assertIn("Hello world", self.sound_monitor.recognizedTexts)

    @patch.object(sr.Recognizer, 'listen')
    @patch.object(sr.Recognizer, 'recognize_google')
    def test_detectViolation_violation(self, mock_recognize, mock_listen):
        """نص يحتوي كلمة مشتبه بها -> مخالفة."""
        mock_listen.return_value = MagicMock()

        # نعيد نص فيه كلمة مشتبه بها (مثلاً "help")
        mock_recognize.return_value = "I need help now"

        violation = self.sound_monitor.detectViolation()
        self.assertTrue(violation)

    # ========== 4) اختبار دالة generateAlert ==========

    @patch('builtins.print')
    def test_generateAlert_violation(self, mock_print):
        """التأكد من طباعة تنبيه المخالفة."""
        self.sound_monitor.generateAlert(True)
        mock_print.assert_called_with("حالة غش: تم رصد كلمات مشتبه بها!")

    @patch('builtins.print')
    def test_generateAlert_no_violation(self, mock_print):
        """التأكد من طباعة عدم وجود مخالفة."""
        self.sound_monitor.generateAlert(False)
        mock_print.assert_called_with("No violation detected this time.")


if __name__ == '__main__':
    unittest.main()