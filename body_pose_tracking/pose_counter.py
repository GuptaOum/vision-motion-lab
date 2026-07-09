# pose_counter.py
import cv2
import mediapipe as mp
import numpy as np

class PoseCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.counter = 0
        self.stage = None
        
    def process_frame(self, frame):
        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect poses
        results = self.pose.process(image)
        
        # Convert the image back to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            # Get landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            
            # Calculate angle
            angle = self.calculate_angle(shoulder, elbow, wrist)
            
            # Counter logic
            if angle > 160:
                self.stage = "down"
            if angle < 30 and self.stage == 'down':
                self.stage = "up"
                self.counter += 1
            
            # Visualize
            cv2.putText(image, f'Reps: {self.counter}', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(image, f'Stage: {self.stage}', (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Draw pose
            mp.solutions.drawing_utils.draw_landmarks(
                image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
        return image
    
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360-angle
        return angle

    def reset_counter(self):
        self.counter = 0