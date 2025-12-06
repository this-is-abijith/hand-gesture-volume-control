import cv2
import mediapipe as mp
import math
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(page_title="AI Volume Control", page_icon="🖐️", layout="wide")

# --- 2. CUSTOM CSS (The "Cyberpunk" UI Look) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
    }
    /* Title Styling */
    h1 {
        color: #00FF94;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 0 0 10px #00FF94;
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    /* Instructions Text */
    .instructions {
        color: #FFFFFF;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. AUDIO LIBRARY SETUP ---
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

try:
    CoInitialize()
except Exception:
    pass

volume = None
minVol, maxVol = -65.0, 0.0

try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange() 
    minVol, maxVol = volRange[0], volRange[1]
except Exception:
    pass # Audio failed, app continues in "Visual Only" mode

# --- 4. MEDIAPIPE SETUP ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# --- 5. PROCESSING CLASS ---
class VolumeController(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        results = hands.process(img_rgb)
        
        # Default bar values
        volBar = 400
        volPer = 0
        
        h, w, c = img.shape

        # Draw a semi-transparent UI box for the volume bar area
        overlay = img.copy()
        cv2.rectangle(overlay, (20, 120), (100, 480), (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Coordinates
                x1, y1 = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
                x2, y2 = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Calculate Distance
                length = math.hypot(x2 - x1, y2 - y1)

                # Interpolation
                vol = np.interp(length, [30, 200], [minVol, maxVol])
                volBar = np.interp(length, [30, 200], [400, 150])
                volPer = np.interp(length, [30, 200], [0, 100])

                # Set Volume
                if volume:
                    try:
                        volume.SetMasterVolumeLevel(vol, None)
                    except:
                        pass

                # Dynamic Color: Green if low volume, Red if high volume
                barColor = (0, 255, 0)
                if volPer > 70:
                    barColor = (0, 0, 255) # Red
                elif volPer > 30:
                    barColor = (0, 165, 255) # Orange

                # Visuals on Hand
                cv2.circle(img, (x1, y1), 12, barColor, cv2.FILLED)
                cv2.circle(img, (x2, y2), 12, barColor, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), barColor, 3)
                cv2.circle(img, (cx, cy), 12, barColor, cv2.FILLED)
                
                if length < 30:
                    cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
                
                # Draw Active Bar with Dynamic Color
                cv2.rectangle(img, (50, int(volBar)), (85, 400), barColor, cv2.FILLED)
                cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_DUPLEX, 1, barColor, 2)

        else:
            # If no hand, show 0% or last state (Optional: reset visuals)
            pass

        # Draw Static Bar Outline
        cv2.rectangle(img, (50, 150), (85, 400), (200, 200, 200), 2)
        cv2.putText(img, 'VOL', (45, 140), cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200), 2)

        return img

# --- 6. STREAMLIT LAYOUT ---

# Sidebar
with st.sidebar:
    st.title("🎛️ Settings")
    st.markdown("Adjust the sensitivity of the AI model.")
    detect_conf = st.slider("Min Detection Confidence", 0.0, 1.0, 0.7)
    track_conf = st.slider("Min Tracking Confidence", 0.0, 1.0, 0.7)
    st.divider()

# Main Content
st.title("AI Gesture Controller")
st.markdown('<p class="instructions">Pinch to Lower Volume | Spread to Increase Volume</p>', unsafe_allow_html=True)

# Columns to center the video
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Frame for the video
    st.markdown("""
    <div style="border: 2px solid #00FF94; padding: 10px; border-radius: 10px;">
    """, unsafe_allow_html=True)
    
    webrtc_streamer(
        key="volume-control", 
        video_transformer_factory=VolumeController,
        media_stream_constraints={"video": True, "audio": False}
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Powered by MediaPipe & OpenCV | Works best with good lighting.")