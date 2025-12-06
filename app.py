import cv2
import mediapipe as mp
import math
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# --- AUDIO CONTROL LIBRARIES ---
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 1. Initialize COM library (Crucial for Streamlit threading)
try:
    CoInitialize()
except Exception as e:
    # Sometimes it's already initialized, so we just ignore the warning
    pass

# 2. Setup Volume Control (Robust Method)
volume = None
minVol = -65.0
maxVol = 0.0

try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange() 
    minVol = volRange[0]
    maxVol = volRange[1]
except Exception as e:
    print(f"Audio Driver Error: {e}")
    # We continue without audio, so the app doesn't crash

# 3. Setup MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# 4. The Processing Class
class VolumeController(VideoTransformerBase):
    def transform(self, frame):
        # Convert frame to numpy array
        img = frame.to_ndarray(format="bgr24")
        
        # Flip and convert to RGB
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        results = hands.process(img_rgb)
        
        # Initialize bar variables
        volBar = 400
        volPer = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get Image Dimensions
                h, w, c = img.shape
                
                # Get Coordinates: Thumb (4) and Index (8)
                x1, y1 = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
                x2, y2 = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Draw Visuals
                cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

                # Calculate Distance
                length = math.hypot(x2 - x1, y2 - y1)

                # Hand Range: 30 (closed) - 200 (open)
                # Volume Range: minVol - maxVol
                vol = np.interp(length, [30, 200], [minVol, maxVol])
                volBar = np.interp(length, [30, 200], [400, 150])
                volPer = np.interp(length, [30, 200], [0, 100])

                # Set Volume (Only if audio setup worked)
                if volume:
                    try:
                        volume.SetMasterVolumeLevel(vol, None)
                    except:
                        pass

                if length < 30:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # Draw Volume Bar
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        return img

# 5. Streamlit UI
st.title("Hand Gesture Volume Control")
webrtc_streamer(key="volume-control", video_transformer_factory=VolumeController)