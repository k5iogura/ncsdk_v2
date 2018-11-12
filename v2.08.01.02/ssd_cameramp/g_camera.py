# Copyright(c) 2018 Kenji.Ogura
# License: Such as Unauthorized use is prohibited.
# mailto : kenji.ogura@jcom.zaq.ne.jp

import time
import multiprocessing as mp

# Import Original NCSDK modules
from video_objects import *

def decode_key(key):
    ascii_code = key & 0xFF
    if ascii_code == ord('q'):
        return False
    return True

def overlay(source_image, result):

    if result is None:
        draw_img(source_image)
        return

    for ibox in range(int(result[0])):
            offset_box = (ibox + 1) * 7
            if (
                    not numpy.isfinite(result[offset_box + 0]) or
                    not numpy.isfinite(result[offset_box + 1]) or
                    not numpy.isfinite(result[offset_box + 2]) or
                    not numpy.isfinite(result[offset_box + 3]) or
                    not numpy.isfinite(result[offset_box + 4]) or
                    not numpy.isfinite(result[offset_box + 5]) or
                    not numpy.isfinite(result[offset_box + 6])
                ):
                continue
            overlay_on_image(source_image, result[offset_box:offset_box + 7])

def draw_img(display_image):
    global resize_output, resize_output_width, resize_output_height
    if (resize_output):
        display_image = cv2.resize(display_image,
                                   (resize_output_width, resize_output_height),
                                   cv2.INTER_LINEAR)
    cv2.imshow(cv_window_name, display_image)
    key = cv2.waitKey(1)
    return key

class video_source:
    def __init__(self,source_mode='UVC', videoDev=0, fps=30 ,w=320, h=240):
        self.source_mode = source_mode
        self.proc = None

        if  self.source_mode == 'PiCamera':
            from imutils.video import VideoStream
            self.video_obj = VideoStream(usePiCamera=True, resolution=(w,h)).start()
            time.sleep(1)   # warm up
            print("video_source : setup PiCamera")
        else:
            import cv2
            self.video_obj = cv2.VideoCapture(videoDev)
            time.sleep(1)   # warm up
            if not self.video_obj.isOpened():
                print("Not found uvc camera /dev/video"+str(videoDev))
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

import cv2
def mp_video_start(run_flag, e_frames, cam_mode, imgQ=None, rsltQ=None, fps=30, w=640, h=480):
    if cam_mode == 1:
        source_mode='PiCamera'
    else:
        source_mode='UVC'
    vs = video_source(source_mode, fps=fps, w=w, h=h).start()
    time.sleep(1)           # warm up
    start =time.perf_counter()
    e_frames.value = 0
    latest_rslt = [ 0 ]
    while run_flag.value == 1:

        img = vs.read()
        if imgQ is not None:
            try:
                if imgQ.full():
                    imgQ.get_nowait()
            except : pass
            imgQ.put(img)

        if rsltQ is not None:
            result = None
            try:
                if not rsltQ.empty():
                    result = rsltQ.get_nowait()
            except : pass
            if result is not None:
                latest_rslt = result

        overlay(img, latest_rslt)
        cv2.imshow('playback',img)
        if cv2.waitKey(1)!= -1:break
        e_frames.value+=1
    vs.release()
    run_flag.value = 0
    print("\nfinish mp_video_start")

