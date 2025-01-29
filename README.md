# AI-ExamIntegrity+

**AI ExamIntegrity+** ensures academic integrity in online exams using AI technologies like facial recognition, face tracking, and sound analysis. It provides real-time monitoring, detects suspicious behaviors, and records data only during violations, balancing security and privacy while adhering to ethical standards.

## 🛡️ Suspicious Behavior Detection System
This project implements a real-time system to monitor and detect suspicious behavior during online activities such as exams. It uses **MediaPipe** for face and eye tracking and **OpenCV** for video processing.

## ✨ Features
- Detects suspicious eye gaze direction (left, right, up).
- Identifies head movements (left, right, up, down).
- Displays behavior status on the screen in real-time.
- Flags suspicious behavior when it exceeds the allowed threshold.

## 📋 Requirements
- **Python 3.12**
- **OpenCV**
- **MediaPipe**
- **NumPy**

---

## 💾 Installation and Setup

### 🖥️ For Windows Users
1. **Install Python**:
   - Download Python from the [official Python website](https://www.python.org/downloads/).
   - During installation, check the box to **Add Python to PATH**.

2. **Install Dependencies**:
   - Open a Command Prompt and run the following commands:
     ```bash
     pip install opencv-python mediapipe numpy
     ```

3. **Clone the Repository**:
   - Download the project code from GitHub or manually copy the code files.

4. **Run the Program**:
   - Open Command Prompt, navigate to the folder containing the code, and run:
     ```bash
     python <filename>.py
     ```
   - Replace `<filename>` with the name of the Python file containing the code.

---

### 🍏 For Mac Users
1. **Install Python**:
   - macOS typically comes with Python pre-installed. To check, open a terminal and run:
     ```bash
     python3 --version
     ```
   - If Python is not installed, download it from the [official Python website](https://www.python.org/downloads/).

2. **Install Homebrew (Optional)**:
   - If you don't have Homebrew installed, you can install it using:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

3. **Install Dependencies**:
   - Open a terminal and run:
     ```bash
     pip3 install opencv-python mediapipe numpy
     ```

4. **Allow Camera Access**:
   - Go to **System Preferences > Security & Privacy > Privacy > Camera** and ensure your terminal or IDE has access to the camera.

5. **Run the Program**:
   - Open a terminal, navigate to the folder containing the code, and run:
     ```bash
     python3 <filename>.py
     ```
   - Replace `<filename>` with the name of the Python file containing the code.

---

## 🔧 Troubleshooting

### ⚠️ Common Errors
1. **`ModuleNotFoundError`**:
   - Ensure all required dependencies are installed. Run:
     ```bash
     pip install opencv-python mediapipe numpy
     ```
   - For Mac users, use `pip3` if `pip` is not recognized.

2. **Camera Not Working**:
   - Check if the camera is in use by another application.
   - Ensure your terminal or IDE has camera access permissions.

3. **Python Not Recognized**:
   - Ensure Python is added to the system PATH (Windows) or use `python3` on macOS.

---

## 🎯 How to Use
1. Run the program.
2. A window will open showing the webcam feed with facial landmarks.
3. The system will monitor for suspicious behavior such as looking away or head movement.
4. Behavior descriptions and warnings will be displayed in real-time on the screen.

---

## 🔍 Notes
- The system assumes a normalized coordinate system for the face. Calibration may be required for different screen setups.
- For best results, ensure adequate lighting and keep the face clearly visible to the camera.

---

## 👨‍💻 Made By
This project, **AI ExamIntegrity+**, was developed by our team as part of our graduation project at **Taibah University, College of Computer Science and Engineering, Department of Computer Science**.

### 🏆 Team Members:
- **Mohammed Magdy Khalifah**  
- **Omar Marwan Salamah**  
- **Abdulrahman Sami Al-Madani**  
- **Abdul Aziz Radhi Al-Mutairi**  
- **Ayoub Abdullah Al Jabri**

📌 **Supervised by:**  
**Dr. Saeed Ibrahim Alqahtani**  

We are grateful for the guidance and support received throughout the development of this project. 🚀