import tkinter as tk
from tkinter import Label, Button
import cv2
import mediapipe as mp
import time
import numpy as np
from threading import Thread

class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exercise Selector")
        self.root.geometry("800x600")

        self.running = False
        self.cap = cv2.VideoCapture(0)
        self.canvas = Label(self.root)
        self.canvas.pack()

        # Buttons for exercise selection
        self.arm_button = Button(self.root, text="Arm Exercise", command=self.start_arm_exercise, width=20)
        self.arm_button.pack(pady=10)

        self.leg_button = Button(self.root, text="Leg Exercise", command=self.start_leg_exercise, width=20)
        self.leg_button.pack(pady=10)

        self.exit_button = Button(self.root, text="Exit", command=self.exit_app, width=20)
        self.exit_button.pack(pady=10)

        # Mediapipe setup
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            model_complexity=1,
        )
        self.stage = None
        self.stage1 = None
        self.counter = 0
        self.counter1 = 0

    def start_arm_exercise(self):
        if not self.running:
            self.running = True
            self.counter = 0
            self.stage = None
            self.exercise_type = "arm"
            Thread(target=self.run_exercise).start()

    def start_leg_exercise(self):
        if not self.running:
            self.running = True
            self.counter1 = 0
            self.stage1 = None
            self.exercise_type = "leg"
            Thread(target=self.run_exercise).start()

    def run_exercise(self):
        while self.running:
            ret, img = self.cap.read()
            if not ret:
                break
            img = cv2.flip(img, 1)
            img = cv2.resize(img, (800, 600))
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            results = self.pose.process(imgRGB)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark

                if self.exercise_type == "arm":
                    self.process_arm_exercise(img, landmarks)
                elif self.exercise_type == "leg":
                    self.process_leg_exercise(img, landmarks)

            # Convert to Tkinter-compatible format
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (800, 600))
            img_tk = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            photo = cv2.imencode(".jpg", img_tk)[1].tobytes()
            self.update_canvas(photo)

            key = cv2.waitKey(1)
            if key & 0xFF == ord("x"):
                break

    def process_arm_exercise(self, img, landmarks):
        mpDraw = mp.solutions.drawing_utils
        mpPose = mp.solutions.pose
        cap = cv2.VideoCapture(0)
        pTime = 0
        stage = None
        stage1 = None
        pose = mpPose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8, model_complexity=1)#mpDraw = mp.solutions.drawing_utils



        fps = cap.get(cv2.CAP_PROP_FPS)
        counter = 0
        def to_pixel_coords(coords):
         """Convert normalized coordinates to pixel coordinates."""
         return int(coords[0] * img.shape[1]), int(coords[1] * img.shape[0])
        def smooth_landmarks(prev, curr):
         return alpha * curr + (1 - alpha) * prev
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
            cv2.imshow("img", img)

            # Key controls
            key = cv2.waitKey(1)
            if key == ord('r'):
                counter = 0
            if key & 0xFF == ord('x'):
                break

        cap.release()
        cv2.destroyAllWindows() 
 
        pass

    def process_leg_exercise(self, img, landmarks):
        mpDraw = mp.solutions.drawing_utils
        mpPose = mp.solutions.pose
        cap = cv2.VideoCapture(0)
        stage = None
        stage1 = None
        pose = mpPose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7,model_complexity=1)#'static_image_mode=False'
        pTime=0
        fps = cap.get(cv2.CAP_PROP_FPS)
        counter = 0
        counter1=0
        def calculate_angle(a, b, c):
            #"""Calculate angle between three points."""
            a = np.array([a.x, a.y])
            b = np.array([b.x, b.y])
            c = np.array([c.x, c.y])
            
            # Vectors
            ab = a - b
            bc = c - b
            
            # Dot product and magnitudes
            dot_product = np.dot(ab, bc)
            magnitude_ab = np.linalg.norm(ab)
            magnitude_bc = np.linalg.norm(bc)
            
            # Cosine of the angle
            cos_theta = dot_product / (magnitude_ab * magnitude_bc)
            cos_theta = np.clip(cos_theta, -1.0, 1.0)  # Avoid precision errors
            
            # Angle in degrees
            angle = np.degrees(np.arccos(cos_theta))
            
            return angle
        def to_pixel_coords(coords):
            """Convert normalized coordinates to pixel coordinates."""
            #coords=np.array([coords.x,coords.y])
            return int(coords.x * img.shape[1]), int(coords.y * img.shape[0])
        """def count_bends(angle, flag, count):
            if angle > 160 and flag != 'down':
                count += 1
                flag = 'down'
            elif angle < 50 and flag == 'down':
                flag = None
            return flag, count"""
        while True:
            yes, img = cap.read()

            img = cv2.flip(img, 1)
            img = cv2.resize(img, (1000, 700))
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            img_shape=img.shape
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

                    angle = calculate_angle(left_hip, left_knee, left_ankle)
                    angle1 = calculate_angle(right_hip, right_knee, right_ankle)
                    # '''flag_left, left_count = count_bends(left_angle, flag_left, left_count)
                    # flag_right, right_count = count_bends(right_angle, flag_right, right_count)'''
                    #left leg
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
                
                    # '''cv2.putText(img, f'Left Count: {left_count}', (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (355, 100, 222), 2, cv2.LINE_AA)
                    # cv2.putText(img, f'Right Count: {right_count}', (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (355, 100, 222), 2, cv2.LINE_AA)'''

                    #mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
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
                #print(f"Error: {e}")
                pass



            # Calculate and display FPS
            cTime = time.time()
            local_time = time.ctime(cTime)
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(local_time), (560, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(img, str(int(fps)), (700, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

            # Display img
            cv2.imshow("img", img)

            # Key controls
            key = cv2.waitKey(1)
            if key == ord('r'):
                counter = 0
                counter1= 0
            if key & 0xFF == ord('x'):
                break

        cap.release()
        cv2.destroyAllWindows()
        pass

    def update_canvas(self, photo):
        # Display the video feed in the Tkinter label
        img = tk.PhotoImage(data=photo)
        self.canvas.configure(image=img)
        self.canvas.image = img

    def exit_app(self):
        self.running = False
        self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseApp(root)
    root.mainloop()
