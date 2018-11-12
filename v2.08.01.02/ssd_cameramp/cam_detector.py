# Copyright(c) 2018 Kenji.Ogura
# License: Such as Unauthorized use is prohibited.
# mailto : kenji.ogura@jcom.zaq.ne.jp

from mvnc import mvncapi as mvnc
import sys
import numpy
import cv2
import time
import csv
import os
import argparse
import sys
from sys import argv
from g_detector import *
from g_camera   import *

# Import Original NCSDK modules
#from video_objects import *

def decode_key(key):
    ascii_code = key & 0xFF
    if ascii_code == ord('q'):
        return False
    return True

def main(args):
    global resize_output, resize_output_width, resize_output_height

    buffsize = 3

    Detector = [ None for i in range(0,buffsize) ]
    for i in range(0,buffsize):
        Detector[i] = detector(callback_func=overlay,used_limit=args.Nset)
        Detector[i].set_preproc(preprocess_image)

    exit_app = False
    which_source = lambda x: 'UVC' if x else 'PiCamera'
    import multiprocessing as mp
    mpQ = mp.Queue(33)
    #cam = video_source(which_source(args.uvc),Queue=mpQ).start()
    cam = video_source(which_source(args.uvc)).start()

    cv2.namedWindow(cv_window_name)
    cv2.moveWindow(cv_window_name, 10,  10)

    for i in range(0,buffsize):
        img = cam.read()
        print(img.shape)
        #img = mpQ.get()
        Detector[i].initiate(img)

    playback_count = predicts_count = 0
    playback_per_second = predicts_per_second = 0
    display_image=[None for i in range(0,buffsize)]
    start_time = time.perf_counter()
    start_frames = Detector[0].frames
    while(True):
        for i in range(0, buffsize):
            try:
                #display_image[i] = mpQ.get()
                display_image[i] = cam.read()
                image_overlapped = Detector[i].finish(display_image[i])
                Detector[i].initiate(display_image[i])
                key = draw_img(image_overlapped)
                if (key != -1):
                    if (decode_key(key) == False):
                        for j in range(0,buffsize): Detector[j].finish(None)
                        exit_app = True
                        break
                playback_count += 1
                if i == 0: predicts_count += 1
            except Exception as e:
                print("Any Exception found:",e.args)
                exit_app = True
                break
        if playback_count > 33:
            end_time = time.perf_counter()
            end_frames = Detector[0].frames
            playback_per_second = playback_count / (end_time - start_time)
            predicts_per_second = (end_frames - start_frames) / (end_time - start_time)
            sys.stdout.write('\b'*20)
            sys.stdout.write("%8.3f/%8.3fFPS"%(predicts_per_second, playback_per_second))
            sys.stdout.flush()

        if exit_app:
            break

    # Clean up the graph and the device
    try:
        for i in range(0, buffsize):
            Detector[i].close()
        cam.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print("all finalizeing faild",e.args)
        sys.exit(1)
    print("\nfinalizing OK playback: %.2fFPS predict: %.2fFPS"%(playback_per_second, predicts_per_second))

import threading
import multiprocessing as mp
if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("-W", "--width" ,  type=int, default=640,  help="video width")
    args.add_argument("-H", "--height",  type=int, default=480,  help="video height")
    args.add_argument("-r", "--resize",  action="store_true",    help="resize window")
    args.add_argument("-u", "--uvc",     action="store_true",    help="Use UVC")
    args.add_argument("-N", "--Nset",    type=int, default=10,   help="limit of Using Nset def=10")
    args = args.parse_args()

    cam_mode = 1    # 1:MIPI Camera
    if args.uvc: cam_mode=0

    Detector = detector(used_limit=args.Nset)
    Detector.set_preproc(preprocess_image)

    imgQ     = mp.Queue(8)
    rsltQ    = mp.Queue(8)
    run_flag = mp.Value('i',1)
    e_frame  = mp.Value('i',0)
    p = mp.Process(
        target=mp_video_start,
        args=(run_flag, e_frame, cam_mode, imgQ, rsltQ),
        daemon=True)
    p.start()

    latest_result = [ 0 for i in range(0,7+7*2) ]

    start = time.perf_counter()
    while True:
        try:
            Detector.initiate(imgQ.get())
            result = Detector.fetch()
            if result is not None:
                latest_result = result
            rsltQ.put(latest_result)

            if run_flag.value == 1:
                if (e_frame.value%33)==0:
                    e_time = time.perf_counter() - start
                    sys.stdout.write('\b'*17)
                    sys.stdout.write("%2d-%2d-%2d:%8.3f"%(latest_result[0],imgQ.qsize(),rsltQ.qsize(),(e_frame.value/e_time)))
                    sys.stdout.flush()
            else:
                break
        except : break

    sys.stdout.write('\n')
    Detector.close()
    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

#    sys.exit(main(args))

