import cv2
import mediapipe as mp
import time
import numpy as np


mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
cap = cv2.VideoCapture(0)
pTime = 0
stage = None
stage1 = None
pose = mpPose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8, model_complexity=1)#'static_image_mode=False'


fps = cap.get(cv2.CAP_PROP_FPS)
counter = 0
def to_pixel_coords(coords):
    """Convert normalized coordinates to pixel coordinates."""
    return int(coords[0] * img.shape[1]), int(coords[1] * img.shape[0])
#def smooth_landmarks(prev, curr):
    #return alpha * curr + (1 - alpha) * prev
def calculate_angle(a, b, c):
    #"""Calculate angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
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

while True:
    yes, img = cap.read()

    img = cv2.flip(img, 1)
    img = cv2.resize(img, (1000, 700))
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    img_shape=img.shape
    results = pose.process(imgRGB)
    try:
      if results.pose_landmarks:
         landmark = results.pose_landmarks.landmark

            # Landmarks for the right arm
         shoulder = [landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
         elbow = [landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
         wrist = [landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].y]

            # Landmarks for the left arm
         shoulder1 = [landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
         elbow1 = [landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].x,
                  landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
         wrist1 = [landmark[mpPose.PoseLandmark.LEFT_WRIST.value].x,
                  landmark[mpPose.PoseLandmark.LEFT_WRIST.value].y]

         # Calculate angles
         angle = calculate_angle(shoulder, elbow, wrist)
         angle1 = calculate_angle(shoulder1, elbow1, wrist1)

         # Count reps for right arm
         if angle > 160:
            stage = "down"
         if angle < 37 and stage == "down":
            stage = "up"
            counter += 1
            print(counter)

         # Count reps for left arm
         if angle1 > 160:
            stage1 = "down"
         if angle1 < 37 and stage1 == "down":
            stage1 = "up"
            counter += 1
            print(counter)
         if 'angle' in locals() and 'angle1' in locals():
          bar = np.interp(angle, (11, 175), (200, 650))
          bar1 = np.interp(angle1, (11, 175), (200, 650))
         else:
           bar=200
           bar1=200
         cv2.putText(img, f'Left Angle: {int(angle)}', (11, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 201, 211), 1, cv2.LINE_AA)
         cv2.putText(img, f'Right Angle: {int(angle1)}', (700, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 201, 211), 1, cv2.LINE_AA)

         # Display counters and stages
         cv2.putText(img, 'REPS', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
         cv2.putText(img, str(counter), (120, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2, cv2.LINE_AA)
         cv2.putText(img, 'STAGE', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
         cv2.putText(img, stage, (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)
         cv2.putText(img, 'STAGE1', (700, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
         cv2.putText(img, stage1, (780, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)
            # Draw progress bars
         cv2.rectangle(img, (100, 200), (200, 650), (0, 255, 0), 2)
         cv2.rectangle(img, (100, int(bar)), (200, 650), (0, 255, 0), cv2.FILLED)
         cv2.rectangle(img, (800, 200), (900, 650), (0, 255, 0), 2)
         cv2.rectangle(img, (800, int(bar1)), (900, 650), (0, 255, 0), cv2.FILLED)

            # Highlight key landmarks and connections
         for point in [shoulder, elbow, wrist, shoulder1, elbow1, wrist1]:
            cv2.circle(img, to_pixel_coords(point), 5, (0, 255, 0), -1)
         cv2.line(img, to_pixel_coords(elbow), to_pixel_coords(shoulder), (200, 0, 0), 2)
         cv2.line(img, to_pixel_coords(elbow), to_pixel_coords(wrist), (200, 0, 0), 2)
         cv2.line(img, to_pixel_coords(elbow1), to_pixel_coords(shoulder1), (200, 0, 0), 2)
         cv2.line(img, to_pixel_coords(elbow1), to_pixel_coords(wrist1), (200, 0, 0), 2)

    except Exception as e:
        print(f"Error: {e}")
        pass

    # Calculate and display FPS
    cTime = time.time()
    local_time = time.ctime(cTime)
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(local_time), (560, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(img, str(int(fps)), (700, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    # Display image
    cv2.imshow("Arm Exercise", img)

    # Key controls
    key = cv2.waitKey(1)
    if key == ord('r'):
        counter = 0
    if key & 0xFF == ord('x'):
        break

cap.release()
cv2.destroyAllWindows() 
