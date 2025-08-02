import cv2
import mediapipe as mp
import pygame
import math

# Initialize pygame mixer
pygame.mixer.init()

# Preload sound files
sound_files = {
    "Sa": pygame.mixer.Sound("Sa.wav"),
    "Ri": pygame.mixer.Sound("Ri.wav"),
    "Ga": pygame.mixer.Sound("Ga.wav"),
    "Ma": pygame.mixer.Sound("Ma.wav"),
    "Pa": pygame.mixer.Sound("Pa.wav"),
    "Da": pygame.mixer.Sound("Dha.wav"),
    "Ni": pygame.mixer.Sound("Ni.wav")
}

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # single hand
mp_draw = mp.solutions.drawing_utils

# Finger tip landmarks
FINGER_TIPS = [4, 8, 12, 16, 20]

# Swara mapping based on finger count
finger_count_to_swara = {
    0: "Sa",  # fist
    1: "Ri",
    2: "Ga",
    3: "Ma",
    4: "Pa",
    5: "Da"
}

# Function to detect OK sign
def is_ok_sign(landmarks):
    # Distance between thumb tip (4) and index tip (8)
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    dist = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

    # Middle, ring, pinky fingers should be up
    middle_up = landmarks[12].y < landmarks[10].y
    ring_up = landmarks[16].y < landmarks[14].y
    pinky_up = landmarks[20].y < landmarks[18].y

    return dist < 0.05 and middle_up and ring_up and pinky_up

last_swara = None

# Capture webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Flip camera horizontally
    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    swara = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Check OK sign first
            if is_ok_sign(hand_landmarks.landmark):
                swara = "Ni"
            else:
                # Count fingers for other swaras
                fingers_up = 0

                # Thumb
                if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                    fingers_up += 1

                # Other fingers
                for tip_id in [8, 12, 16, 20]:
                    if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                        fingers_up += 1

                swara = finger_count_to_swara.get(fingers_up)

    # Display swara on screen
    if swara:
        cv2.putText(frame, f"Swara: {swara}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # Play sound only if changed
        if swara != last_swara:
            pygame.mixer.stop()
            sound_files[swara].play()
            last_swara = swara
    else:
        last_swara = None

    cv2.imshow("Carnatic Swara Player", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
