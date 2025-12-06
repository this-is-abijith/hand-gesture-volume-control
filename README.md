# 🖐️ AI Virtual Mouse & Volume Controller

A Computer Vision application that uses hand gestures to control the system volume in real-time. Built with **Python**, **MediaPipe**, and **Streamlit**.

## 🚀 Features
- **Real-time Hand Tracking:** Uses Google's MediaPipe framework for low-latency landmark detection.
- **Gesture Recognition:** Calculates the Euclidean distance between the thumb and index finger to determine interaction.
- **System Integration:** Directly controls the Windows Master Volume using `pycaw`.
- **Visual Feedback:** Provides an on-screen volume bar and percentage indicator.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Computer Vision:** OpenCV, MediaPipe
- **GUI Framework:** Streamlit (WebRTC)
- **Audio Control:** Pycaw, Comtypes

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/hand-gesture-volume-control.git](https://github.com/YOUR_USERNAME/hand-gesture-volume-control.git)
   cd hand-gesture-volume-control
2. **Install dependencies**
```bash
  pip install -r requirements.txt
```
3. **🏃‍♂️ How to Run**
Run the application using Streamlit:
```bash
streamlit run app.py
```
A browser window will open. Grant permission for the camera, and the tracking will start immediately.

📐 How it Works (The Math)
Landmark Detection: The model detects 21 hand landmarks.

Distance Calculation: We calculate the length between the Thumb Tip (4) and Index Finger Tip (8).

Interpolation: The distance (pixels) is mapped to the volume range (dB) using linear interpolation (numpy.interp).

Pinch (Close) → 0% Volume

Spread (Far) → 100% Volume

⚠️ Notes
This application currently supports Windows OS only (due to pycaw dependencies).

Lighting conditions may affect tracking accuracy.

🤝 Contributing
Feel free to fork this project and submit pull requests. You can also open issues for bugs or feature suggestions.

Created by ABIJITH BINU
