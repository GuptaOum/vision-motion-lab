import cv2
import mediapipe as mp
import time
import numpy as np
from tkinter import *
from threading import Thread
import os
import tensorflow as tf

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose

# Global variables
exercise_running = False
exercise_running1 = False
cap = None
cap1 = None
reps_memory = {"arm": 0, "leg": 0, "leg1":0}  # Persistent memory for exercise repetitions

# GUI labels for reps
arm_reps_label = None
leg_reps_label = None
leg_reps_label1= None


def update_gui_reps():
    """Update the GUI with the current reps for each exercise."""
    if arm_reps_label:
        arm_reps_label.config(text=f"Arm Reps: {reps_memory['arm']}")
    if leg_reps_label:
        leg_reps_label.config(text=f"Leg Reps: {reps_memory['leg']}")
    if leg_reps_label1:
        leg_reps_label1.config(text=f"Leg Reps: {reps_memory['leg1']}")


def close_camera():
    """Safely close the camera and release resources."""
    global cap, exercise_running
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    exercise_running = False
    cap=None


def close_camera1():
    """Safely close the camera and release resources."""
    global cap1, exercise_running1
    if cap1 is not None:
        cap1.release()
    cv2.destroyAllWindows()
    exercise_running1 = False
    cap1=None


def reset_exercise_variables():
    """Reset variables to default values when switching exercises."""
    global exercise_running, exercise_running1, cap, cap1
    exercise_running = False
    exercise_running1 = False
    if cap is not None:
        cap.release()
    if cap1 is not None:
        cap1.release()
    cap = None
    cap1 = None 
def start_arm_exercise():
    """Run the Arm Exercise."""
    global exercise_running, cap
    reset_exercise_variables()  # Reset previous exercise variables
    if exercise_running:
        return  # Prevent multiple instances

    exercise_running = True
    cap = cv2.VideoCapture(os.path.join(ASSETS_DIR, "Bicep Curl.mp4"))
    pTime = 0
    stage = None
    stage1 = None
    counter = reps_memory["arm"]  # Start from saved reps

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
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        try:
            if results.pose_landmarks:
                landmark = results.pose_landmarks.landmark

                # Right arm landmarks
                shoulder = [landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,
                            landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].x,
                         landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].y]
                shoulder1 = [landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow1 = [landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].x,
                  landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist1 = [landmark[mpPose.PoseLandmark.LEFT_WRIST.value].x,
                  landmark[mpPose.PoseLandmark.LEFT_WRIST.value].y]

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)
                angle1= calculate_angle(shoulder1, elbow1, wrist1)
                # Count reps
                if angle > 160:
                    stage = "down"
                if angle < 37 and stage == "down":
                    stage = "up"
                    counter += 1
                    reps_memory["arm"] = counter  # Update memory
                    update_gui_reps()
                    print(f"Arm Reps: {counter}")
                if angle1 > 160:
                    stage1 = "down"
                if angle1 < 37 and stage1 == "down":
                    stage1 = "up"
                    counter += 1
                    reps_memory["arm"] = counter  # Update memory
                    update_gui_reps()
                    print(f"Arm Reps: {counter}")
                if 'angle' in locals() and 'angle1' in locals():
                 bar = np.interp(angle, (11, 175), (200, 650))
                 bar1 = np.interp(angle1, (11, 175), (200, 650))
                else:
                 bar=200
                 bar1=200
                cv2.putText(img, f'Left Angle: {int(angle)}', (11, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 201, 0), 2, cv2.LINE_AA)
                cv2.putText(img, f'Right Angle: {int(angle1)}', (700, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 201, 0), 2, cv2.LINE_AA)

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
        cv2.imshow("Arm Exercise", img)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('x'):
         break
        if key==ord('r'):
         counter=0
         reps_memory["arm"] = counter  # Update memory
         update_gui_reps()
    close_camera()
def start_leg_exercise():
    """Run the Leg Exercise."""
    global exercise_running1, cap1
    reset_exercise_variables()  # Reset previous exercise variables
    
    if exercise_running1:
        return  # Prevent multiple instances

    exercise_running1 = True
    cap1 = cv2.VideoCapture(0)
    pTime = 0
    stage = None
    stage1= None
    counter = reps_memory["leg"] 
    counter1= reps_memory["leg1"] # Start from saved reps

    pose = mpPose.Pose(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        model_complexity=1,
    )
    def to_pixel_coords(coords):
     """Convert normalized coordinates to pixel coordinates."""
     #coords=np.array([coords.x,coords.y])
     return int(coords.x * img.shape[1]), int(coords.y * img.shape[0])
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

    while True:
        success, img = cap1.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1000, 700))
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
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

                # Calculate angle
                angle = calculate_angle(left_hip, left_knee, left_ankle)
                angle1 = calculate_angle(right_hip, right_knee, right_ankle)

                # Count reps
                if angle > 160:
                    stage = "down"
                if angle < 50 and stage == "down":
                    stage = "up"
                    counter += 1
                    reps_memory["leg"] = counter  # Update memory
                    update_gui_reps()
                    print(f"Leg Reps: {counter}")
                #count right
                if angle1 > 160:
                    stage1 = "down"
                if angle1 < 50 and stage1 == "down":
                    stage1 = "up"
                    counter1 += 1
                    reps_memory["leg1"] = counter1  # Update memory
                    update_gui_reps()
                    print(f"Leg Reps: {counter1}")
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
            print(f"Error: {e}")
            pass

        cTime = time.time()
        local_time = time.ctime(cTime)
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(local_time), (560, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, str(int(fps)), (700, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        #Display Image
        cv2.imshow("Leg Exercise", img)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('x'):
         break
        if key==ord('r'):
         counter=0
         counter1=0
         reps_memory["leg"] = counter  # Update memory for left leg
         reps_memory["leg1"] = counter1  # Update memory for right leg
         update_gui_reps()

    close_camera1()


from tkinter import *
from threading import Thread
import os

# Updated UI for the Exercise Application
def open_gui():
    global arm_reps_label, leg_reps_label, leg_reps_label1

    root = Tk()
    root.geometry("600x500")
    root.title("Exercise Tracker(VS)")
    root.config(bg="#1E1E1E")

    # Title Label
    title_label = Label(
        root,
        text="Exercise TrackerVS",
        font=("Helvetica", 18, "bold"),
        fg="white",
        bg="#1E1E1E"
    )
    title_label.pack(pady=15)

    # Exercise Button Section
    button_frame = Frame(root, bg="#1E1E1E")
    button_frame.pack(pady=10)

    def select_button(selected_button):
        """Highlight the selected button."""
        for btn in [arm_button, leg_button]:
            btn.config(bg="#444", fg="white")  # Reset colors
        selected_button.config(bg="#32CD32", fg="black")  # Highlight selected

    arm_button = Button(
        button_frame,
        text="Arm Exercise",
        command=lambda: [select_button(arm_button), Thread(target=start_arm_exercise).start()],
        width=20,
        font=("Arial", 14, "bold"),
        bg="#444",
        fg="white",
        activebackground="#32CD32",
        activeforeground="black"
    )
    arm_button.grid(row=0, column=0, padx=10, pady=10)

    leg_button = Button(
        button_frame,
        text="Leg Exercise",
        command=lambda: [select_button(leg_button), Thread(target=start_leg_exercise).start()],
        width=20,
        font=("Arial", 14, "bold"),
        bg="#444",
        fg="white",
        activebackground="#32CD32",
        activeforeground="black"
    )
    leg_button.grid(row=0, column=1, padx=10, pady=10)

    # Reps Section
    reps_frame = Frame(root, bg="#1E1E1E")
    reps_frame.pack(pady=15)

    arm_reps_label = Label(
        reps_frame,
        text=f"Arm Reps: {reps_memory['arm']}",
        font=("Helvetica", 12),
        fg="white",
        bg="#1E1E1E"
    )
    arm_reps_label.grid(row=0, column=0, padx=10, pady=5)

    leg_reps_label = Label(
        reps_frame,
        text=f"Left Leg Reps: {reps_memory['leg']}",
        font=("Helvetica", 12),
        fg="white",
        bg="#1E1E1E"
    )
    leg_reps_label.grid(row=1, column=0, padx=10, pady=5)

    leg_reps_label1 = Label(
        reps_frame,
        text=f"Right Leg Reps: {reps_memory['leg1']}",
        font=("Helvetica", 12),
        fg="white",
        bg="#1E1E1E"
    )
    leg_reps_label1.grid(row=2, column=0, padx=10, pady=5)

    # Status Section
    status_frame = Frame(root, bg="#1E1E1E")
    status_frame.pack(pady=10)

    status_label = Label(
        status_frame,
        text="Status: Waiting",
        font=("Helvetica", 12),
        fg="#FFD700",
        bg="#1E1E1E"
    )
    status_label.pack()

    def update_status(new_status):
        """Update the status label with a new status."""
        status_label.config(text=f"Status: {new_status}")

    # Control Buttons
    control_frame = Frame(root, bg="#1E1E1E")
    control_frame.pack(pady=20)

    def reset_reps():
        """Reset all reps to zero and update the GUI."""
        reps_memory['arm'] = 0
        reps_memory['leg'] = 0
        reps_memory['leg1'] = 0
        update_gui_reps()
        update_status("Reps reset successfully.")

    reset_button = Button(
        control_frame,
        text="Reset Reps",
        command=reset_reps,
        width=15,
        font=("Arial", 12),
        bg="#FFD700",
        fg="black",
        activebackground="#FFC107"
    )
    reset_button.grid(row=0, column=0, padx=10)

    exit_button = Button(
        control_frame,
        text="Exit",
        command=lambda: close_or_exit(root),
        width=15,
        font=("Arial", 12, "bold"),
        bg="#FF6347",
        fg="white",
        activebackground="#FF4500"
    )
    exit_button.grid(row=0, column=1, padx=10)

    def close_or_exit(window):
        """Close the application safely."""
        if exercise_running or exercise_running1:
            close_exercise_camera()
        else:
            window.destroy()

    def close_exercise_camera():
        """Close the camera if an exercise is running."""
        if exercise_running:
            close_camera()
        elif exercise_running1:
            close_camera1()

    # Finalize and run the GUI
    root.mainloop()

if __name__ == "__main__":
    open_gui()