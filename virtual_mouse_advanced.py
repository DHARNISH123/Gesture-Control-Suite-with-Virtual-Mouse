import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import sys

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Screen size
screen_width, screen_height = pyautogui.size()
prev_x, prev_y = 0, 0
smoothening = 7
safe_margin = 10
clicking = False

# Initialize Volume Control
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))

    vol_range = volume_ctrl.GetVolumeRange()
    min_vol = vol_range[0]
    max_vol = vol_range[1]
except Exception as e:
    print(f"Volume control not initialized: {e}")
    volume_ctrl = None
    min_vol, max_vol = 0, 0

# Initialize Webcam
cap = cv2.VideoCapture(0)

def get_landmarks_position(landmarks, img_w, img_h, index):
    x = int(landmarks[index].x * img_w)
    y = int(landmarks[index].y * img_h)
    return x, y

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            handedness = "Right" if idx == 0 else "Left"

            index_x, index_y = get_landmarks_position(lm, img_w, img_h, 8)
            middle_x, middle_y = get_landmarks_position(lm, img_w, img_h, 12)
            thumb_x, thumb_y = get_landmarks_position(lm, img_w, img_h, 4)

            dist_thumb_index = np.linalg.norm(np.array([index_x - thumb_x, index_y - thumb_y]))
            dist_index_middle = np.linalg.norm(np.array([index_x - middle_x, index_y - middle_y]))

            if handedness == "Right":
                x_screen = np.interp(lm[8].x, [0, 1], [0, screen_width])
                y_screen = np.interp(lm[8].y, [0, 1], [0, screen_height])
                curr_x = prev_x + (x_screen - prev_x) / smoothening
                curr_y = prev_y + (y_screen - prev_y) / smoothening
                curr_x = np.clip(curr_x, safe_margin, screen_width - safe_margin)
                curr_y = np.clip(curr_y, safe_margin, screen_height - safe_margin)
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                if dist_thumb_index < 30:
                    pyautogui.click()
                    cv2.circle(img, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                    time.sleep(0.2)

                elif dist_index_middle < 30:
                    pyautogui.rightClick()
                    cv2.circle(img, (index_x, index_y), 15, (255, 0, 0), cv2.FILLED)
                    time.sleep(0.3)

                elif dist_thumb_index > 80 and dist_index_middle < 40:
                    pyautogui.scroll(-10)
                    cv2.putText(img, "Scrolling", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

                elif dist_thumb_index < 20 and not clicking:
                    pyautogui.mouseDown()
                    clicking = True
                    cv2.putText(img, "Drag Start", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                elif dist_thumb_index > 50 and clicking:
                    pyautogui.mouseUp()
                    clicking = False
                    cv2.putText(img, "Drag End", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                # Volume Control
                if volume_ctrl:
                    vol = np.interp(dist_thumb_index, [20, 150], [min_vol, max_vol])
                    volume_ctrl.SetMasterVolumeLevel(vol, None)
                    vol_display = int(np.interp(vol, [min_vol, max_vol], [0, 100]))
                    cv2.putText(img, f"Volume: {vol_display}%", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            elif handedness == "Left":
                try:
                    bright = np.interp(dist_thumb_index, [20, 150], [10, 100])
                    sbc.set_brightness(int(bright))
                    cv2.putText(img, f"Brightness: {int(bright)}%", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                except Exception as e:
                    cv2.putText(img, "Brightness Error", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Virtual Mouse Advanced", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
