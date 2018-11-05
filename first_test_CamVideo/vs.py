from imutils.video import VideoStream
from imutils.video import FPS
import numpy
import cv2
import time

vs = VideoStream(usePiCamera=True).start()
time.sleep(1)
fps= FPS().start()

while True:
    img = vs.read()
    cv2.imshow("Video", img)
    if cv2.waitKey(100) != -1: break
    fps.update()
fps.stop()
vs.stop()
cv2.destroyAllWindows()

print("%.6f"%(fps.elapsed()))
print("%.2f"%(fps.fps()))
