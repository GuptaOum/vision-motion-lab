import cv2
import numpy as np
import mediapipe as mp
import time

# Mediapipe Pose Initialization
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8,model_complexity=1)

# Initialize Video Capture
cap = cv2.VideoCapture(0)
pTime = 0
stage = None
stage1 = None
counter = 0

# Smoothing parameters
alpha = 0.5  # For exponential moving average smoothing
prev_landmarks = None  # Stores previous landmarks for smoothing

# FPS from the camera
fps = cap.get(cv2.CAP_PROP_FPS)

# Helper function: Calculate angle between three points
def calculate_angle(a, b, c):
    
    
    # Vectors
    ab = a - b
    bc = c - b
    
    # Dot product and magnitudes
    dot_product = np.dot(ab, bc)
    magnitude_ab = np.linalg.norm(ab)
    magnitude_bc = np.linalg.norm(bc)
    
    # Cosine of the angle
    cos_theta = dot_product / (magnitude_ab * magnitude_bc + 1e-7)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)  # Avoid precision errors
    
    # Angle in degrees
    angle = np.degrees(np.arccos(cos_theta))
    return angle

# Helper function: Convert normalized Mediapipe coordinates to pixel coordinates
def to_pixel_coords(coords, img_shape):
   
    return int(coords.x * img_shape[1]), int(coords.y * img_shape[0])

# Smoothing function for landmark positions
def smooth_landmarks(prev, curr):
    return alpha * curr + (1 - alpha) * prev

# Main processing loop
while True:
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    img = cv2.resize(img, (1000, 700))
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = pose.process(imgRGB)
    img_shape = img.shape

    try:
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Initialize smoothed landmarks if first frame
            if prev_landmarks is None:
                prev_landmarks = [np.array([lm.x, lm.y]) for lm in landmarks]
            else:
                smoothed_landmarks = [
                    smooth_landmarks(prev_landmarks[i], np.array([landmarks[i].x, landmarks[i].y]))
                    for i in range(len(landmarks))
                ]
                prev_landmarks = smoothed_landmarks
            
            # Get body part positions
             # Get body part positions using smoothed landmarks
            left_hip = smoothed_landmarks[mpPose.PoseLandmark.LEFT_HIP.value]
            left_knee = smoothed_landmarks[mpPose.PoseLandmark.LEFT_KNEE.value]
            left_ankle = smoothed_landmarks[mpPose.PoseLandmark.LEFT_ANKLE.value]
            right_hip = smoothed_landmarks[mpPose.PoseLandmark.RIGHT_HIP.value]
            right_knee = smoothed_landmarks[mpPose.PoseLandmark.RIGHT_KNEE.value]
            right_ankle = smoothed_landmarks[mpPose.PoseLandmark.RIGHT_ANKLE.value]
            left_hip1 = landmarks[mpPose.PoseLandmark.LEFT_HIP.value]
            left_knee1 = landmarks[mpPose.PoseLandmark.LEFT_KNEE.value]
            left_ankle1 = landmarks[mpPose.PoseLandmark.LEFT_ANKLE.value]
            right_hip1 = landmarks[mpPose.PoseLandmark.RIGHT_HIP.value]
            right_knee1 = landmarks[mpPose.PoseLandmark.RIGHT_KNEE.value]
            right_ankle1 = landmarks[mpPose.PoseLandmark.RIGHT_ANKLE.value]

            
            # Calculate angles
            angle = calculate_angle(left_hip, left_knee, left_ankle)
            angle1 = calculate_angle(right_hip, right_knee, right_ankle)
            
            # Progress bars
            bar = np.interp(angle, (40, 160), (200, 650))
            bar1 = np.interp(angle1, (40, 160), (200, 650))

            # Count repetitions for left leg
            if angle > 160:
                stage = "down"
            if angle < 45 and stage == "down":
                stage = "up"
                counter += 1

            # Count repetitions for right leg
            if angle1 > 160:
                stage1 = "down"
            if angle1 < 45 and stage1 == "down":
                stage1 = "up"
                counter += 1

            # Draw progress bars
            cv2.rectangle(img, (100, 200), (200, 650), (0, 255, 0), 2)
            cv2.rectangle(img, (100, int(bar1)), (200, 650), (0, 255, 0), cv2.FILLED)
            cv2.rectangle(img, (800, 200), (900, 650), (0, 255, 0), 2)
            cv2.rectangle(img, (800, int(bar)), (900, 650), (0, 255, 0), cv2.FILLED)
            
            # Highlight key landmarks and connections
            for point in [left_hip1 ,left_knee1, left_ankle1, right_hip1, right_knee1, right_ankle1]:
                cv2.circle(img, to_pixel_coords(point, img_shape), 5, (0, 255, 0), -1)
            cv2.line(img, to_pixel_coords(left_hip1, img_shape), to_pixel_coords(left_knee1, img_shape), (255, 0, 0), 2)
            cv2.line(img, to_pixel_coords(left_knee1, img_shape), to_pixel_coords(left_ankle1, img_shape), (255, 0, 0), 2)
            cv2.line(img, to_pixel_coords(right_hip1, img_shape), to_pixel_coords(right_knee1, img_shape), (255, 0, 0), 2)
            cv2.line(img, to_pixel_coords(right_knee1, img_shape), to_pixel_coords(right_ankle1, img_shape), (255, 0, 0), 2)

    except Exception as e:
        pass

    # Display info
    cv2.putText(img, f'Counter: {counter}', (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, f'Left Angle: {int(angle1) if "angle" in locals() else 0}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, f'Right Angle: {int(angle) if "angle1" in locals() else 0}', (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Display image
    cv2.imshow("Pose Tracking", img)

    # Key controls
    key = cv2.waitKey(1)
    if key == ord('r'):
        counter = 0
    if key & 0xFF == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()
