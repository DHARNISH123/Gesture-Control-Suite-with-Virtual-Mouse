import cv2
import mediapipe as mp
import numpy as np
import keyboard
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
screen_w, screen_h = 640, 480

# Gesture cooldown settings
prev_gesture_time = time.time()
gesture_cooldown = 1.0  # seconds

# Gesture stabilization
gesture_history = []
gesture_max_length = 5

def get_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def update_gesture_history(new_gesture):
    if len(gesture_history) >= gesture_max_length:
        gesture_history.pop(0)
    gesture_history.append(new_gesture)
    return gesture_history.count(new_gesture) > gesture_max_length // 2

def perform_gesture_action(gesture, current_time):
    global prev_gesture_time
    if current_time - prev_gesture_time > gesture_cooldown:
        if gesture == "Play/Pause":
            keyboard.press_and_release('k')
        elif gesture == "Volume Up":
            keyboard.press_and_release('up')
        elif gesture == "Volume Down":
            keyboard.press_and_release('down')
        elif gesture == "Next Video":
            keyboard.press_and_release('shift+n')
        elif gesture == "Previous Video":
            keyboard.press_and_release('shift+p')
        prev_gesture_time = current_time

def detect_gesture(lm, img_w, img_h):
    index_finger = (int(lm[8].x * img_w), int(lm[8].y * img_h))
    middle_finger = (int(lm[12].x * img_w), int(lm[12].y * img_h))
    thumb_tip = (int(lm[4].x * img_w), int(lm[4].y * img_h))

    thumb_index_dist = get_distance(thumb_tip, index_finger)
    index_middle_dist = get_distance(index_finger, middle_finger)

    # Gestures logic
    if index_middle_dist > 60 and thumb_index_dist > 60:
        return "Play/Pause"
    elif thumb_index_dist < 30:
        return "Volume Up"
    elif thumb_index_dist > 80:
        return "Volume Down"
    elif index_finger[0] > img_w - 100:
        return "Next Video"
    elif index_finger[0] < 100:
        return "Previous Video"
    else:
        return None

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_h, img_w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    current_time = time.time()
    gesture_name = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            gesture = detect_gesture(lm, img_w, img_h)

            if gesture:
                if update_gesture_history(gesture):
                    perform_gesture_action(gesture, current_time)
                    gesture_name = gesture

    if gesture_name:
        cv2.putText(img, gesture_name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    cv2.imshow("YouTube Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
