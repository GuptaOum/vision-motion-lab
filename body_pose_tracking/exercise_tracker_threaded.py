import cv2
import mediapipe as mp
import time
import numpy as np
from tkinter import *
from threading import Thread
import os

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose

# Global variables
exercise_running = False 
exercise_running1= False # To track if an exercise is running
cap = None  # Video capture object
cap1=None

def close_camera():
    """Safely close the camera and release resources."""
    global cap, exercise_running
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    exercise_running = False
def close_camera1():
    """Safely close the camera and release resources."""
    global cap1, exercise_running1
    if cap1 is not None:
        cap1.release()
    cv2.destroyAllWindows()
    exercise_running1 = False


def start_arm_exercise():
    """Run the Arm Exercise."""
    global exercise_running , cap
    if exercise_running:
        return  # Prevent multiple instances

    exercise_running = True
    cap = cv2.VideoCapture(0)
    pTime = 0
    stage = None
    stage1 = None
    counter = 0
    
    pose = mpPose.Pose(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        model_complexity=1,
    )
    def to_pixel_coords(coords):
     """Convert normalized coordinates to pixel coordinates."""
     return int(coords[0] * img.shape[1]), int(coords[1] * img.shape[0])
    def calculate_angle(a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        ab = a - b
        bc = c - b
        dot_product = np.dot(ab, bc)
        magnitude_ab = np.linalg.norm(ab)
        magnitude_bc = np.linalg.norm(bc)
        cos_theta = dot_product / (magnitude_ab * magnitude_bc + 1e-7)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        return np.degrees(np.arccos(cos_theta))
    
    while True:
        success, img = cap.read()
        if not success:
            break
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

    close_camera()


def start_leg_exercise():
    """Run the Leg Exercise."""
    global exercise_running1, cap1
    if exercise_running1:
        return  # Prevent multiple instances

    exercise_running1 = True
    cap1 = cv2.VideoCapture(0)
    pTime = 0
    stage = None
    stage1= None
    counter = 0
    counter1=0

    pose = mpPose.Pose(
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8,
        model_complexity=1,
    )

    def calculate_angle(a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        ab = a - b
        bc = c - b
        dot_product = np.dot(ab, bc)
        magnitude_ab = np.linalg.norm(ab)
        magnitude_bc = np.linalg.norm(bc)
        cos_theta = dot_product / (magnitude_ab * magnitude_bc + 1e-7)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        return np.degrees(np.arccos(cos_theta))
    def to_pixel_coords(coords):
     """Convert normalized coordinates to pixel coordinates."""
     #coords=np.array([coords.x,coords.y])
     return int(coords.x * img.shape[1]), int(coords.y * img.shape[0])
    while True:
        success, img = cap1.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1000, 700))
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        results = pose.process(imgRGB)

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                left_hip = landmarks[mpPose.PoseLandmark.LEFT_HIP.value]
                left_knee = landmarks[mpPose.PoseLandmark.LEFT_KNEE.value]
                left_ankle = landmarks[mpPose.PoseLandmark.LEFT_ANKLE.value]
                right_hip = landmarks[mpPose.PoseLandmark.RIGHT_HIP.value]
                right_knee = landmarks[mpPose.PoseLandmark.RIGHT_KNEE.value]
                right_ankle = landmarks[mpPose.PoseLandmark.RIGHT_ANKLE.value]
               #angle
                angle = calculate_angle(left_hip, left_knee, left_ankle)
                angle1 = calculate_angle(right_hip, right_knee, right_ankle)

                # Calculate angle
                if angle > 160:
                 stage = "down"
                if angle < 50 and stage == "down":
                 stage = "up"
                 counter += 1
                 print(counter)

             # Count reps for right leg
                if angle1 > 160:
                 stage1 = "down"
                if angle1 < 50 and stage1 == "down":
                 stage1 = "up"
                 counter1 += 1
                 print(counter1)

                # Display info
                '''cv2.putText(img, f'Angle: {int(angle)}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(img, f'Reps: {counter}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)'''
                if 'angle' in locals() and 'angle1' in locals():
                 bar = np.interp(angle, (45, 170), (200, 650))
                 bar1 = np.interp(angle1, (45, 170), (200, 650))
                else:
                 bar=200
                 bar1=200
                cv2.putText(img, f'Left Angle: {int(angle1)}', (11, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 211), 2, cv2.LINE_AA)
                cv2.putText(img, f'Right Angle: {int(angle)}', (700, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 211), 2, cv2.LINE_AA)

                cv2.putText(img, 'REPS', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(img, str(counter1), (120, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(img, 'REPS1', (700, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(img, str(counter), (780, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2, cv2.LINE_AA)

                cv2.putText(img, 'STAGE1', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(img, stage1, (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(img, 'STAGE', (700, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(img, stage, (780, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)

                    # Draw progress bars
                cv2.rectangle(img, (100, 200), (200, 650), (0, 255, 0), 2)
                cv2.rectangle(img, (100, int(bar1)), (200, 650), (0, 255, 0), cv2.FILLED)
                cv2.rectangle(img, (800, 200), (900, 650), (0, 255, 0), 2)
                cv2.rectangle(img, (800, int(bar)), (900, 650), (0, 255, 0), cv2.FILLED)

                # Highlight key landmarks and connections
                for point in [left_hip, left_knee, left_ankle, right_hip, right_knee, right_ankle]:
                    cv2.circle(img, to_pixel_coords(point), 5, (0, 255, 0), -1)
                cv2.line(img, to_pixel_coords(left_knee), to_pixel_coords(left_hip), (200, 0, 0), 2)
                cv2.line(img, to_pixel_coords(left_knee), to_pixel_coords(left_ankle), (200, 0, 0), 2)
                cv2.line(img, to_pixel_coords(right_knee), to_pixel_coords(right_hip), (200, 0, 0), 2)
                cv2.line(img, to_pixel_coords(right_knee), to_pixel_coords(right_ankle), (200, 0, 0), 2)
   
        except Exception as e:
            pass
        cTime = time.time()
        local_time = time.ctime(cTime)
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(local_time), (560, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, str(int(fps)), (700, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        #Display Image
        cv2.imshow("Leg Exercise", img)
        #key controls
        key = cv2.waitKey(1)
        if key == ord('r'):
         counter = 0
         counter1= 0
        if key & 0xFF == ord('x'):
         break
    close_camera1()


def open_gui():
    """Create the GUI."""
    root = Tk()
    root.geometry("300x200")  # Smaller geometry
    root.title("Exercise Selector")
    
    # Store references to buttons
    arm_button = None
    leg_button = None

    # Define button state change function
    def select_button(selected_button):
        # Reset all buttons to their default color
        arm_button.config(bg="#F0F0F0")
        leg_button.config(bg="#F0F0F0")

        # Set the selected button to green
        selected_button.config(bg="#32CD32")
    
    Label(root, text="Choose an Exercise", font=("Arial", 14)).pack(pady=10)
    
    # Buttons
    arm_button = Button(
        root,
        text="Arm Exercise",
        command=lambda: [select_button(arm_button), Thr ead(target=start_arm_exercise).start()],
        width=20,
        font=("Arial", 12), 
    )
    arm_button.pack(pady=5)

    leg_button = Button(
        root,
        text="Leg Exercise",
        command=lambda: [select_button(leg_button), Thread(target=start_leg_exercise).start()],
        width=20,
         font=("Arial", 12),
    )
    leg_button.pack(pady=5)

    Button(
        root,
        text="Exit",
        command=lambda: (close_camera(), close_camera1(), root.destroy(),cv2.destroyAllWindows(),os._exit(0)),
        width=20,
        bg="#FF6347",
        fg="white",
        font=("Arial", 12, "bold")
    ).pack(pady=5)
    
    root.mainloop()



if __name__ == "__main__":
    open_gui()
