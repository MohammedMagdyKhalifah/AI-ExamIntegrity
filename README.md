# AI-ExamIntegrity+ 🚀

**AI-ExamIntegrity+** is an advanced system designed to ensure academic integrity during online exams. It integrates two primary modules:

1. **Speech Recognition Module 🎤**: Captures and transcribes live audio (supporting both English and Arabic) using Google's Speech Recognition API.
2. **Suspicious Behavior Detection Module 👀**: Utilizes real-time facial landmark detection via MediaPipe and OpenCV to monitor eye gaze and head movements, flagging any suspicious behavior.

Both modules work together to provide a comprehensive monitoring solution for secure and fair online examinations.

---

## Table of Contents 📑
- [Features ✨](#features)
- [Requirements 📋](#requirements)
- [Installation and Setup 🛠️](#installation-and-setup)
  - [Windows 💻](#windows)
  - [macOS 🍏](#macos)
- [Usage 🔧](#usage)
- [Troubleshooting ⚠️](#troubleshooting)
- [Credits 🙌](#credits)

---

## Features ✨

- **Speech Recognition**
  - Real-time audio capture from the microphone.
  - Transcribes speech in English and Arabic.
  - Handles ambient noise and recognition errors gracefully.

- **Suspicious Behavior Detection**
  - Real-time facial landmark detection using MediaPipe.
  - Monitors eye gaze and head movement.
  - Flags suspicious behavior if deviations exceed preset thresholds.
  - Displays visual feedback on the video feed.

---

## Requirements 📋

- **Python**: Version 3.12 or later
- **For Speech Recognition Module**:
  - [`speech_recognition`](https://pypi.org/project/SpeechRecognition/)
  - [`PyAudio`](https://pypi.org/project/PyAudio/) *(for microphone input)*

- **For Suspicious Behavior Detection Module**:
  - [`opencv-python`](https://pypi.org/project/opencv-python/)
  - [`mediapipe`](https://pypi.org/project/mediapipe/)
  - [`numpy`](https://pypi.org/project/numpy/)

- **Hardware & Other Requirements**:
  - A working **webcam** (for video capture) 📷.
  - A functioning **microphone** (for audio capture) 🎙️.
  - **Internet connection** (required by the speech recognition API) 🌐.

---

## Installation and Setup 🛠️

### Windows 💻

1. **Install Python**:
   - Download the latest Python installer from the [official Python website](https://www.python.org/downloads/).
   - During installation, make sure to **Add Python to PATH**.

2. **Install Dependencies**:
   - Open Command Prompt and run:
     ```bash
     pip install speechrecognition pyaudio opencv-python mediapipe numpy
     ```
   - **Note**: If you experience issues installing `PyAudio`, you may need to download a precompiled wheel from [PyAudio Unofficial Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it with:
     ```bash
     pip install PyAudio‑<version>‑cp312‑cp312m‑win_amd64.whl
     ```

3. **Clone or Download the Repository**:
   - **Clone via Git**:
     ```bash
     git clone https://github.com/MohammedMagdyKhalifah/AI-ExamIntegrity.git
     ```
   - Or download the ZIP archive directly from your repository page and extract it.

4. **Run the Program**:
   - Open Command Prompt, navigate to the project directory, and run:
     ```bash
     python <filename>.py
     ```
   - Replace `<filename>.py` with the desired module file name:
     - For the speech recognition module (e.g., `speech_recognition_module.py`)
     - For the suspicious behavior detection module (e.g., `suspicious_behavior_detector.py`)

---

### macOS 🍏

1. **Install Python**:
   - macOS usually comes with Python pre-installed; however, it is recommended to install the latest version from the [official Python website](https://www.python.org/downloads/).
   - Verify your Python installation:
     ```bash
     python3 --version
     ```

2. **Install Homebrew (Optional but Recommended)**:
   - If you do not have Homebrew, install it using:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

3. **Install Dependencies**:
   - Open Terminal and run:
     ```bash
     pip3 install speechrecognition opencv-python mediapipe numpy
     ```
   - **For PyAudio**:
     - First, install PortAudio using Homebrew:
       ```bash
       brew install portaudio
       ```
     - Then install PyAudio:
       ```bash
       pip3 install pyaudio
       ```

4. **Allow Camera Access**:
   - Go to **System Preferences > Security & Privacy > Privacy > Camera** and ensure that your Terminal or IDE is granted camera access.

5. **Clone or Download the Repository**:
   - **Clone via Git**:
     ```bash
     git clone https://github.com/MohammedMagdyKhalifah/AI-ExamIntegrity.git
     ```
   - Alternatively, download the ZIP archive from your repository and extract it.

6. **Run the Program**:
   - Open Terminal, navigate to the project directory, and execute:
     ```bash
     python3 <filename>.py
     ```
   - Replace `<filename>.py` with the appropriate file name for the module you wish to run.

---

## Usage 🔧

### Speech Recognition Module 🎤
1. Run the speech recognition module (e.g., `speech_recognition_module.py`).
2. The program will prompt: **"Say something in English or Arabic..."**
3. Speak clearly into your microphone.
4. The application will attempt to transcribe your speech in both English and Arabic. If it fails to understand, it will display a message asking you to try again.

### Suspicious Behavior Detection Module 👀
1. Run the suspicious behavior detection module (e.g., `suspicious_behavior_detector.py`).
2. A window will open displaying the webcam feed along with facial landmarks.
3. The system will continuously analyze eye gaze and head movement:
   - It displays descriptive messages (e.g., "Looking Left", "Head Moved Up") on the screen.
   - If suspicious behavior persists beyond the allowed threshold, a warning is shown.
4. Press the `Esc` key to exit the program.

---

## Troubleshooting ⚠️

### Common Issues

- **ModuleNotFoundError**:
  - Verify that all required dependencies are installed. If not, run:
    ```bash
    pip install speechrecognition pyaudio opencv-python mediapipe numpy
    ```
  - On macOS, substitute `pip` with `pip3` if necessary.

- **Camera Not Working**:
  - Ensure that no other application is using the webcam.
  - Check camera permissions in your operating system settings.

- **Microphone Issues**:
  - Confirm that the microphone is connected and not used by another program.
  - If ambient noise is high, consider adjusting the settings or your environment.

- **PyAudio Installation Errors**:
  - On Windows, try using a precompiled wheel.
  - On macOS, ensure that PortAudio is installed via Homebrew before installing PyAudio.

---

## Credits 🙌

**AI-ExamIntegrity+** was developed to help maintain academic integrity during online examinations.

### Team Members:
- **Mohammed Magdy Khalifah**
- **Omar Marwan Salamah**
- **Abdulrahman Sami Al-Madani**
- **Abdul Aziz Radhi Al-Mutairi**
- **Ayoub Abdullah Al Jabri**

**Supervised by:**  
Dr. Saeed Ibrahim Alqahtani

---

Happy Monitoring! 🚀