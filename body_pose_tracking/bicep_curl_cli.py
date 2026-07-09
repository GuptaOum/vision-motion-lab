import cv2
import mediapipe as mp
import time
import numpy as np
print("enter 1 for LEFT ARM BICEP CURL")
print("enter 2 for RIGHT ARM BICEP CURL")
print("enter 3 for BOTH ARM BICEP CURL")
val = input("Enter") 
if val=='1':
 print("LEFT ARM BICEP CURL") 
elif val=='2':
 print("RIGHT ARM BICEP CURL") 
elif val=='3':
 print("BOTH ARM BICEP CURL") 
else:
  print("YOU SHOULD ENTER VALUE RANGING 1 TO 3")
var=val
if var=='1':
 mpDraw = mp.solutions.drawing_utils
 mpPose = mp.solutions.pose
 def calculate_angle(a,b,c):
  a = np.array(a) 
  b = np.array(b) 
  c = np.array(c)
  radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
  angle = np.abs(radians*180.0/np.pi)
  if angle >180.0:
     angle = 360-angle
  return angle  
 cap = cv2.VideoCapture(0)  
 pTime = 0
 counter=0
 stage=None
 pose = mpPose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
 while True:
     yes, img = cap.read()
    
     img = cv2.flip(img,1)
     img = cv2.resize(img, (1000, 700)) 
     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

     results = pose.process(imgRGB)
     try:
       landmark=results.pose_landmarks.landmark                                                                       
   
       shoulder = [landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
       elbow = [landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
       wrist = [landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].x,landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].y]
       angle = calculate_angle(shoulder, elbow, wrist)
       
            
       if (angle > 160 ):
        stage = "down"
       if ((angle < 30 and stage =='down')):
        stage="up"
        counter+=1
        print(counter)  
     except:
        pass 
        # Setup status box
     #cv2.rectangle(img, (50,50), (250,120), (245,117,16), -1)
        
        # Rep data
     cv2.putText(img, 'REPS', (50,120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, str(counter), 
                    (120,130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,0), 2, cv2.LINE_AA)
        
    
     cv2.putText(img, 'STAGE', (50,60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, stage, (120,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 2, cv2.LINE_AA)
        
     #render ko detect kry gha
     mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 0, 0 ),thickness=2, circle_radius=2), mpDraw.DrawingSpec(color=(255, 255,255 ),thickness=2, circle_radius=2))
     cv2.putText(img, str(angle), (np.multiply(elbow, [640, 480]).astype(int)),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
      
     cTime = time.time()
     local_timet=time.ctime(cTime)
     fps = 1 / (cTime - pTime)
     pTime = cTime
    
     #cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 0), 2)
     cv2.putText(img,str(str(local_timet)),(650,680),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
    
     cv2.imshow("img", img)
    
     if cv2.waitKey(1)& 0xFF == ord('q'):
       break  
     for lnd in mpPose.PoseLandmark:
       print(lnd)
     print(landmark[mpPose.PoseLandmark.NOSE.value] ,"hh")
     print(mpPose.PoseLandmark.NOSE.value ,"hh")
 cap.release()
 cv2.destroyAllWindows()
elif var=='2':
 mpDraw = mp.solutions.drawing_utils
 mpPose = mp.solutions.pose
 def calculate_angle(a,b,c):
  a = np.array(a) 
  b = np.array(b) 
  c = np.array(c) 
  radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
  angle = np.abs(radians*180.0/np.pi)
  if angle >180.0:
     angle = 360-angle
  return angle  
 cap = cv2.VideoCapture(0)  
 pTime = 0
 counter=0
 stage=None
 pose = mpPose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
 while True:
     yes, img = cap.read()
    
     img = cv2.flip(img,1)
     img = cv2.resize(img, (1000, 700)) 
     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

     results = pose.process(imgRGB)
     try:
       landmark=results.pose_landmarks.landmark
   
       shoulder = [landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
       elbow = [landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].x,landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
       wrist = [landmark[mpPose.PoseLandmark.LEFT_WRIST.value].x,landmark[mpPose.PoseLandmark.LEFT_WRIST.value].y]
       angle = calculate_angle(shoulder, elbow, wrist)
       

            
       
       if (angle > 160 ):
        stage = "down"
       if ((angle < 30 and stage =='down')):
        stage="up"
        counter+=1
        print(counter)  
     except:
        pass 
        # Setup status box
     #cv2.rectangle(img, (0,0), (50,50), (245,117,16), )
        
        # Rep data
     cv2.putText(img, 'REPS', (50,120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, str(counter), 
                    (120,130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,0), 2, cv2.LINE_AA)
        
    
     cv2.putText(img, 'STAGE', (50,60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, stage, (120,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 2, cv2.LINE_AA)
        
     #render ko detect kry gha
     mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 0, 0 ),thickness=2, circle_radius=2), mpDraw.DrawingSpec(color=(255, 255,255 ),thickness=2, circle_radius=2))
     cv2.putText(img, str(angle), (np.multiply(elbow, [640, 480]).astype(int)),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
     
     cTime = time.time()
     local_timet=time.ctime(cTime)
     fps = 1 / (cTime - pTime)
     pTime = cTime
    
     #cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 0), 2)
     cv2.putText(img,str(str(local_timet)),(650,680),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),1)
    
     cv2.imshow("img", img)
    
     if cv2.waitKey(1)& 0xFF == ord('q'):
       break  
     #for lnd in mpPose.PoseLandmark:
      # print(lnd)
     #print(landmark[mpPose.PoseLandmark.NOSE.value])
     #print(mpPose.PoseLandmark.NOSE.value)
 cap.release()
 cv2.destroyAllWindows()
elif var=='3':
 mpDraw = mp.solutions.drawing_utils
 mpPose = mp.solutions.pose
 def calculate_angle(a,b,c):
  a = np.array(a) 
  b = np.array(b) 
  c = np.array(c) 
  radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
  angle = np.abs(radians*180.0/np.pi)
  if angle >180.0:
     angle = 360-angle
  return angle  
 def calculate_angle2(a,b,c):
  a = np.array(a) # First
  b = np.array(b) # Mid
  c = np.array(c) # End
  radians2 = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
  angle2 = np.abs(radians2*180.0/np.pi)
  if angle2 >180.0:
     angle2 = 360-angle2
  return angle2
 cap = cv2.VideoCapture(0)  
 pTime = 0
 counter=0
 stage=None
 pose = mpPose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)
 while True:
     yes, img = cap.read()
    
     img = cv2.flip(img,1)
     img = cv2.resize(img, (1000, 700)) 
     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

     results = pose.process(imgRGB)
     try:
       landmark=results.pose_landmarks.landmark
   
       shoulder = [landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
       elbow = [landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].x,landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
       wrist = [landmark[mpPose.PoseLandmark.LEFT_WRIST.value].x,landmark[mpPose.PoseLandmark.LEFT_WRIST.value].y]
       shoulder2 = [landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
       elbow2 = [landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
       wrist2 = [landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].x,landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].y]

       angle = calculate_angle(shoulder, elbow, wrist)
       angle2 = calculate_angle2(shoulder2, elbow2, wrist2)      
            
       cv2.putText(img, str(angle), (np.multiply(elbow, [640, 480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (225,225,0), 1, cv2.LINE_AA)
       cv2.putText(img, str(angle2), (np.multiply(elbow2, [640, 480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (225,225,0), 1, cv2.LINE_AA)
       if ((angle > 160 )and(angle2>160)):
        stage = "down"
       if ((angle < 30 and stage =='down')and(angle2 < 30 and stage =='down')):
        stage="up"
        counter+=1
        print(counter)  
     except:
        pass 
        # Setup status box
     #cv2.rectangle(img, (0,0), (50,50), (245,117,16), )
        
        # Rep data
     cv2.putText(img, 'REPS', (50,120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, str(counter), 
                    (120,130), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,0), 2, cv2.LINE_AA)
        
    
     cv2.putText(img, 'STAGE', (50,60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
     cv2.putText(img, stage, (120,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 2, cv2.LINE_AA)
        
     #render ko detect kry gha
     mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 0, 0 ),thickness=2, circle_radius=2), mpDraw.DrawingSpec(color=(255, 255,255 ),thickness=2, circle_radius=2))
     cTime = time.time()
     local_timet=time.ctime(cTime)
     fps = 1 / (cTime - pTime)
     pTime = cTime
    
     #cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 0), 2)
     cv2.putText(img,str(str(local_timet)),(650,680),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),1)
    
     cv2.imshow("img", img)
    
     if cv2.waitKey(1)& 0xFF == ord('q'):
       break  
     #for lnd in mpPose.PoseLandmark:
      # print(lnd)
     #print(landmark[mpPose.PoseLandmark.NOSE.value])
     #print(mpPose.PoseLandmark.NOSE.value)
 cap.release()
 cv2.destroyAllWindows()