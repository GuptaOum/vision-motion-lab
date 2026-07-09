import cv2
import mediapipe as mp
import time
import numpy as np

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
cap = cv2.VideoCapture(0)
pTime = 0
stage=None
stage1=None

global landmark
global angle
global angle1
global bar
global bar1

fps=cap.get(cv2.CAP_PROP_FPS)

counter=0

def calculate_angle(a,b,c):
  
  a = np.array(a) 
  b = np.array(b) 
  c = np.array(c)
  radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
  angle = np.abs(radians*180.0/np.pi)
  if angle >180.0:
     angle = 360-angle
  return angle  
pose = mpPose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)

while True:
   yes, img = cap.read()
    
   img = cv2.flip(img,1)
   img = cv2.resize(img, (1000 , 700)) 
   imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

   results = pose.process(imgRGB)
   try: 
      landmark=results.pose_landmarks.landmark                                                                       
      
      shoulder = [landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
      elbow = [landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,landmark[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
      wrist = [landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].x,landmark[mpPose.PoseLandmark.RIGHT_WRIST.value].y]
      shoulder1=[landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,landmark[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
      elbow1=[landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].x,landmark[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
      wrist1= [landmark[mpPose.PoseLandmark.LEFT_WRIST.value].x,landmark[mpPose.PoseLandmark.LEFT_WRIST.value].y]
      angle = calculate_angle(shoulder, elbow, wrist)
      angle1=calculate_angle(shoulder1,elbow1,wrist1)
      
            
      if (angle > 160 ):
         stage = "down"
      if(angle1>160):
            stage1= "down"
      if ((angle < 30 and stage =='down')):
         stage="up"
         counter+=1
         print(counter)   
      if ((angle1 < 30 and stage1 =='down')):
         stage1="up"
         counter+=1
         print(counter) 
   
   except:
     pass
   bar=np.interp(angle,(11,175),(200,650))
   bar1=np.interp(angle1,(11,175),(200,650))
   cv2.putText(img, 'REPS', (50,120), 
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
   cv2.putText(img, str(counter), 
                  (120,130), 
                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,0), 2, cv2.LINE_AA)
      
   
   cv2.putText(img, 'STAGE', (50,60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
   cv2.putText(img, stage, (120,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 2, cv2.LINE_AA)
   cv2.putText(img, 'STAGE1', (700,60),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2, cv2.LINE_AA)
   cv2.putText(img, stage1, (780,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 2, cv2.LINE_AA)
      
   #sary render ko detect kry gha 
   #mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS, mpDraw.DrawingSpec(color=(0, 0, 0 ),thickness=2, circle_radius=2), mpDraw.DrawingSpec(color=(255, 255,255 ),thickness=2, circle_radius=2))
   
   
      
   cv2.rectangle(img,(96,200),(154,650),(0,255,0),2)
   cv2.rectangle(img,(100,int(bar)),(150,650),(0,255,0),cv2.FILLED)
   cv2.rectangle(img,(796,200),(854,650),(0,255,0),2)
   cv2.rectangle(img,(800,int(bar1)),(850,650),(0,255,0),cv2.FILLED)
   cv2.circle(img,(np.multiply(elbow, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.circle(img,(np.multiply(shoulder, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.circle(img,(np.multiply(wrist, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.circle(img,(np.multiply(elbow1, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.circle(img,(np.multiply(shoulder1, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.circle(img,(np.multiply(wrist1, [1000, 700]).astype(int)), 5, (0,255,0),2, )
   cv2.line(img,(np.multiply(elbow, [1000, 700]).astype(int)),(np.multiply(shoulder, [1000, 700]).astype(int)),(200,0,0),2)
   cv2.line(img,(np.multiply(elbow, [1000, 700]).astype(int)),(np.multiply(wrist, [1000, 700]).astype(int)),(200,0,0),2)
   cv2.line(img,(np.multiply(elbow1, [1000, 700]).astype(int)),(np.multiply(shoulder1, [1000, 700]).astype(int)),(200,0,0),2)
   cv2.line(img,(np.multiply(elbow1, [1000, 700]).astype(int)),(np.multiply(wrist1, [1000, 700]).astype(int)),(200,0,0),2)
   
   
   cTime = time.time()
   local_timet=time.ctime(cTime)
   fps = 1 / (cTime - pTime)
   pTime = cTime
   
   #cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 0), 2)
   cv2.putText(img,str(str(local_timet)),(560,680),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
   cv2.putText(img,str(int(fps)),(700,600),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255),2)
   cv2.putText(img, str(angle), (np.multiply(elbow, [640, 480]).astype(int)),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,100), 1, cv2.LINE_AA)
   cv2.putText(img, str(angle1), (np.multiply(elbow1, [940, 480]).astype(int)),cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,100), 1, cv2.LINE_AA)
      
   
   cv2.imshow("img", img)
   
   key=  cv2.waitKey(1)
   if key==ord('r'):
         counter=0
   if key & 0xFF == ord('x') :
      break 
      
   #for lnd in mpPose.PoseLandmark:
      # print(lnd)
   #print(landmark[mpPose.PoseLandmark.NOSE.value])
   #print(mpPose.PoseLandmark.NOSE.value)

def findposition(img):
      lmList = []
        
      for ld,ln in enumerate(landmark):
             h, w, c = img.shape
             print(h,w)
             print( ld,ln,'h')
             cx, cy = int(ln.x*w), int(ln.y*h)
             lmList.append([ld, cx, cy])
                
      return lmList
      
lmList = findposition(img)
print(lmList)
cap.release()
cv2.destroyAllWindows()