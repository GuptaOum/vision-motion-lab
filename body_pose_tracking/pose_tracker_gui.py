import cv2
import mediapipe as mp
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox

# Initialize Mediapipe utilities
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Global variables for both functionalities
p_time = 0
stage_arm = None
stage_leg = None
left_count = 0
right_count = 0
arm_counter = 0

# Function to calculate angle
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle

# Function to count repetitions
def count_reps(angle, stage, count):
    if angle > 160 and stage != "down":
        stage = "down"
    elif angle < 75 and stage == "down":
        stage = "up"
        count += 1
    return stage, count

# Function to handle arm tracking
def track_arms():
    global arm_counter, stage_arm
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1000, 700))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        try:
            landmark = results.pose_landmarks.landmark
            # Right arm
            shoulder = [landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, 
                        landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, 
                     landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, 
                     landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Count reps
            stage_arm, arm_counter = count_reps(angle, stage_arm, arm_counter)

            # Display counters and stage
            cv2.putText(img, f'Reps: {arm_counter}', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(img, f'Stage: {stage_arm}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        except:
            pass

        # Show the image
        cv2.imshow("Arm Tracking", img)

        key = cv2.waitKey(1)
        if key == ord('r'):  # Reset counter
            arm_counter = 0
            stage_arm = None
        if key == ord('z'):  # Exit
            break
    cap.release()
    cv2.destroyAllWindows()

# Function to handle leg tracking
def track_legs():
    global left_count, right_count, stage_leg
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1000, 700))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

        try:
            landmark = results.pose_landmarks.landmark
            # Left leg
            left_hip = [landmark[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
                        landmark[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmark[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 
                         landmark[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 
                          landmark[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate angle
            left_angle = calculate_angle(left_hip, left_knee, left_ankle)

            # Count reps
            stage_leg, left_count = count_reps(left_angle, stage_leg, left_count)

            # Display counters and stage
            cv2.putText(img, f'Reps: {left_count}', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(img, f'Stage: {stage_leg}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        except:
            pass

        # Show the image
        cv2.imshow("Leg Tracking", img)

        key = cv2.waitKey(1)
        if key == ord('r'):  # Reset counter
            left_count = 0
            stage_leg = None
        if key == ord('z'):  # Exit
            break
    cap.release()
    cv2.destroyAllWindows()

# GUI setup
def main_gui():
    root = tk.Tk()
    root.title("Pose Tracker")
    root.geometry("400x300")

    tk.Label(root, text="Pose Tracking Application", font=("Helvetica", 16)).pack(pady=20)

    tk.Button(root, text="Track Arms", command=track_arms, font=("Helvetica", 12), width=20).pack(pady=10)
    tk.Button(root, text="Track Legs", command=track_legs, font=("Helvetica", 12), width=20).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit, font=("Helvetica", 12), width=20).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
