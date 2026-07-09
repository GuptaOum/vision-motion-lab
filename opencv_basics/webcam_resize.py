import cv2
import numpy as np
import matplotlib.pyplot as plt
cap = cv2.VideoCapture(0)
while True:
 
 success , image = cap.read()
# Loading the image
 
 image = cv2.resize(image, (500, 500), fx = 0.1, fy = 0.1)
 
 cv2.imshow('frame', image)
 
 if cv2.waitKey(1)& 0xFF == ord('q'):
     break
cap.release()
cv2.destroyAllWindows() 