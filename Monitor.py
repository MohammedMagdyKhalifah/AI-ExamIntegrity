import subprocess
import sys

if __name__ == "__main__":

    # تشغيل الملف FaceMonitor.py
    process_project = subprocess.Popen([sys.executable, "FaceMonitor.py"])
    # تشغيل الملف SoundMonitor.py
    process_audio = subprocess.Popen([sys.executable, "SoundMonitor.py"])

    # الانتظار حتى تنتهي كلتا العمليتين (اختياري)
    process_audio.wait()
    process_project.wait()