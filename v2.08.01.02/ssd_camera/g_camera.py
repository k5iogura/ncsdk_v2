import time

class video_source:
    def __init__(self,source_mode='UVC', deviceNo=0, fps= 30,w=320, h=240):
        self.source_mode = source_mode

        if  self.source_mode == 'PiCamera':
            from imutils.video import VideoStream
            self.video_obj = VideoStream(usePiCamera=True).start()
            time.sleep(1)   # warm up
            print("video_source : setup PiCamera")
        else:
            import cv2
            self.video_obj = cv2.VideoCapture(deviceNo)
            time.sleep(1)   # warm up
            if not self.video_obj.isOpened():
                print("Not found uvc camera /dev/video"+str(deviceNo))
                quit()
            self.video_obj.set(cv2.CAP_PROP_FPS,fps)
            self.video_obj.set(cv2.CAP_PROP_FRAME_WIDTH,w)
            self.video_obj.set(cv2.CAP_PROP_FRAME_HEIGHT,h)
            print("video_source : setup UVC as default %dfps %d/%d"%(fps,w,h))

    def start(self):
        return self

    def read(self):
        if self.source_mode == 'UVC':
            ret, image = self.video_obj.read()
            if not ret:
                print("Cannot read from video source opencv")
                quit()
        else:
            image = self.video_obj.read()
        return image

    def release(self):
        if self.source_mode == 'UVC':
            self.video_obj.release()
        else:
            self.video_obj.stop()

