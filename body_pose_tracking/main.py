# main.py
import cv2
from pose_counter import PoseCounter

print("Starting program...")

# Initialize the webcam
cap = cv2.VideoCapture(0)
print("Camera initialized")

# Initialize the pose counter
counter = PoseCounter()
print("Pose Counter initialized")

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
        
    # Process the frame
    processed_frame = counter.process_frame(frame)
    
    # Display the frame
    cv2.imshow('Exercise Counter', processed_frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()
print("Program ended")