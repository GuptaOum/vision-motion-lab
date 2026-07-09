import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    """Calculate the angle between three points."""
    a = np.array(a)  # First point
    b = np.array(b)  # Middle point
    c = np.array(c)  # Last point

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

# Initialize Mediapipe Holistic and Drawing tools
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Mediapipe holistic configuration
holistic = mp_holistic.Holistic(min_detection_confidence=0.7, min_tracking_confidence=0.7,model_complexity=1)

# Variables to store counters
left_right_count = 0

# Variables to track direction changes
prev_left_right = "neutral"

# Increased threshold angle for head turns
LEFT_RIGHT_THRESHOLD = 20  # Degrees for left-right motion

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb_frame)

    if results.pose_landmarks:
        # Extract key landmarks for head pose estimation
        nose = [
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * frame.shape[1],
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * frame.shape[0]
        ]
        left_ear = [
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].x * frame.shape[1],
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_EAR].y * frame.shape[0]
        ]
        right_ear = [
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].x * frame.shape[1],
            results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_EAR].y * frame.shape[0]
        ]

        # Calculate angles for head movements
        horizontal_angle = calculate_angle(left_ear, nose, right_ear)

        # Detect left-right motion
        if horizontal_angle > 90 + LEFT_RIGHT_THRESHOLD:
            direction = "Right"
        elif horizontal_angle < 90 - LEFT_RIGHT_THRESHOLD:
            direction = "Left"
        else:
            direction = "neutral"

        # Count only when moving from neutral to a direction
        if prev_left_right != direction and direction != "neutral":
            left_right_count += 1

        # Update previous direction
        prev_left_right = direction

        # Draw landmarks on the frame
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
        )

    # Display counts on the frame
    cv2.putText(frame, f"Left-Right Turns: {int(left_right_count/2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show the frame
    cv2.imshow('Head Turn Counter', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()