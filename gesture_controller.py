import cv2
import mediapipe as mp
import subprocess
import numpy as np
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Finger tip landmarks
TIP_IDS = [4, 8, 12, 16, 20]

def count_fingers(lm_list):
    fingers = []
    
    # Thumb
    if lm_list[TIP_IDS[0]][0] > lm_list[TIP_IDS[0] - 1][0]:  # Right hand
        fingers.append(1)
    else:
        fingers.append(0)
    
    # Other 4 fingers
    for id in range(1, 5):
        if lm_list[TIP_IDS[id]][1] < lm_list[TIP_IDS[id] - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers.count(1)

def run_mode(script_name):
    try:
        subprocess.run(["python", f"modes/{script_name}"])
    except Exception as e:
        print(f"Error running {script_name}: {e}")

cap = cv2.VideoCapture(0)
mode_started = False

print("🖐️  Show gesture to select mode:")
print(" 1️⃣  1 finger  = Virtual Mouse")
print(" 2️⃣  2 fingers = YouTube Control")
print(" 3️⃣  3 fingers = Presentation Control")
print(" ✊  Fist       = Exit")

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    lm_list = []
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = img.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))
    
    if lm_list:
        fingers_up = count_fingers(lm_list)

        cv2.putText(img, f"Fingers: {fingers_up}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        if not mode_started:
            if fingers_up == 1:
                print("Launching Virtual Mouse Mode...")
                run_mode("virtual_mouse.py")
                mode_started = True
            elif fingers_up == 2:
                print("Launching YouTube Control Mode...")
                run_mode("youtube_control.py")
                mode_started = True
            elif fingers_up == 3:
                print("Launching Presentation Control Mode...")
                run_mode("presentation_control.py")
                mode_started = True
            elif fingers_up == 0:
                print("Exiting...")
                break

        # Wait before next detection to prevent repeated triggering
        if mode_started:
            time.sleep(2)
            mode_started = False

    cv2.imshow("Gesture Mode Selector", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
