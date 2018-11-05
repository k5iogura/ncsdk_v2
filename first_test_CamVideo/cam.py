import cv2
import numpy as np
import time

cam=cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cv2.namedWindow("camera")

while(1):
    start = time.time()
    (ret, img) = cam.read()
    if ret == False:
        print(img.shape)
    cv2.imshow("camera",img)
    key = cv2.waitKey(15)
    if key != -1: break
    end   = time.time()
    #print('%5.3f\b\b\b\b\b'%(1./(end-start)))
