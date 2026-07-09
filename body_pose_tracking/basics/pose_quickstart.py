import cv2
import mediapipe as mp

oum = mp.solutions.pose
oummodel = oum.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
while True:
    
    success, image = cap.read()
 
    image = cv2.resize(image, (1000, 700)) 
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = oummodel.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks,oum.POSE_CONNECTIONS,mp_drawing.DrawingSpec(color=(142, 68, 173 ),thickness=2, circle_radius=2),
                              mp_drawing.DrawingSpec(color=(229, 29, 81 ),thickness=2, circle_radius=2) )
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = image.shape
            print(id, lm)
            cx, cy = int(lm.x * w), int(lm.y * h)
            
    cv2.imshow("Landmarks", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()