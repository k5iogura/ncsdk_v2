import sys
from imutils.video import VideoStream
from imutils.video import FPS
import  multiprocessing as mp
import numpy
import cv2
import time

class VSX:
    def __init__(self, mpQ):
        #self.vs = VideoStream(usePiCamera=True, framerate=64, resolution=(1088,720)).start()
        self.vs = VideoStream(usePiCamera=True, framerate=64, resolution=(640,480)).start()
        time.sleep(1)
        self.mpQ = mpQ
        self.count = 0
        self.started = time.perf_counter()

    def start(self):
        while True:
            imgX = img = self.vs.read()
            try:
                if self.mpQ.full():
                    self.mpQ.get()
                self.mpQ.put(img)
            except Exception as e:
                print("exp: ",e.args)

            cv2.imshow("Video", imgX)
            if cv2.waitKey(1) != -1: break
            self.count += 1
            if self.count % 33 == 0:
                self.end = time.perf_counter()
                sys.stdout.write('\b'*24)
                sys.stdout.write("%9.3fsec %7.3fFPS"%(self.end-self.started, self.count/(self.end-self.started)))
                sys.stdout.flush()
        self.vs.stop()
        cv2.destroyAllWindows()
        return self

    def stop(self):
        self.vs.stop()
        cv2.destroyAllWindows()

if __name__=="__main__":

    frameQ=mp.Queue(9)
    vsx=VSX(frameQ).start()
    vsx.stop()
