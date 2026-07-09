import cv2
import mediapipe as mp

# Initialize MediaPipe
mpHands = mp.solutions.hands
mpDraw = mp.solutions.drawing_utils
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Finger tip and joint indices
fingerCoordinates = [(8, 6), (12, 10), (16, 14), (20, 18)]  # index, middle, ring, pinky
thumbCoordinate = (4, 2)

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

      # Flip for mirror view
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handIndex, handLms in enumerate(results.multi_hand_landmarks):
            # Draw landmarks
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # --- Hand label correction ---
            handLabel = results.multi_handedness[handIndex].classification[0].label
            if handLabel == "Left":
                handLabel = "Right"
            else:
                handLabel = "Left"

            # Collect points
            h, w, _ = img.shape
            handPoints = [(int(lm.x * w), int(lm.y * h)) for lm in handLms.landmark]

            # Bounding box
            x_coords = [p[0] for p in handPoints]
            y_coords = [p[1] for p in handPoints]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            # Draw rectangle
            cv2.rectangle(img, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)
            cv2.putText(img, f"{handLabel} Hand", (x_min - 20, y_min - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw landmark points
            for point in handPoints:
                cv2.circle(img, point, 3, (0, 0, 255), cv2.FILLED)

            # Count fingers
            upCount = 0
            for tip, joint in fingerCoordinates:
                if handPoints[tip][1] < handPoints[joint][1]:  # finger open
                    upCount += 1

            # Thumb detection (corrected with new handLabel)
            if handLabel == "Right":
                if handPoints[thumbCoordinate[0]][0] > handPoints[thumbCoordinate[1]][0]:
                    upCount += 1
            else:  # Left hand
                if handPoints[thumbCoordinate[0]][0] < handPoints[thumbCoordinate[1]][0]:
                    upCount += 1

            # Show finger count inside bounding box
            cv2.putText(img, f"Fingers: {upCount}", (x_min, y_max + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Finger Counter", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
