# Copyright(c) 2018 Kenji.Ogura
# License: Such as Unauthorized use is prohibited.
# mailto : kenji.ogura@jcom.zaq.ne.jp

import sys
import multiprocessing
import numpy
import cv2
import time
import csv
import os
import argparse
import sys
from sys import argv
from g_camera   import *
from video_objects import *

cv_window_name = "Performace Test for Camera"

def draw_img(display_image):
    global resize_output, resize_output_width, resize_output_height
    if (resize_output):
        display_image = cv2.resize(display_image,
                                   (resize_output_width, resize_output_height),
                                   cv2.INTER_LINEAR)
    cv2.imshow(cv_window_name, display_image)
    key = cv2.waitKey(1)
    return key

def decode_key(key):
    ascii_code = key & 0xFF
    if ascii_code == ord('q'):
        return False
    return True

def main(uvc,width,height):

    exit_app = False
    which_source = lambda x: 'UVC' if x else 'PiCamera'
    cam = video_source(which_source(uvc), w=width, h=height).start()

    cv2.namedWindow(cv_window_name)
    cv2.moveWindow(cv_window_name, 600,  200)

    playback_count = predicts_count = 0
    playback_per_second = predicts_per_second = 0
    start_time = time.perf_counter()
    while(True):
        try:
            display_image = cam.read()
            key = draw_img(display_image)
            if (key != -1):
                if (decode_key(key) == False):
                    exit_app = True
                    break
            playback_count += 1
        except Exception as e:
            print("Any Exception found:",e.args)
            exit_app = True
            break
        if (playback_count % 33) == 0:
            end_time = time.perf_counter()
            playback_per_second = playback_count / (end_time - start_time)
            sys.stdout.write('\b'*20)
            sys.stdout.write("%8.3fFPS"%(playback_per_second))
            sys.stdout.flush()

    # Clean up the graph and the device
    try:
        cam.release()
        cv2.destroyAllWindows()
    except : pass
    print("\nfinalizing OK playback: %.2fFPS predict: %.2fFPS"%(playback_per_second, predicts_per_second))

if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("-W", "--width" ,  type=int, default=640,  help="video width")
    args.add_argument("-H", "--height",  type=int, default=480,  help="video height")
    args.add_argument("-r", "--resize",  action="store_true",    help="resize window")
    args.add_argument("-u", "--uvc",     action="store_true",    help="Use UVC")
    args.add_argument("-m", "--main",    action="store_true",    help="Run on Main Process")
    args.add_argument("-N", "--Nset",    type=int, default=10,   help="limit of Using Nset def=10")
    args = args.parse_args()
    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

    print("Image size %d %d"%(args.width, args.height))
    if args.main:
        print("Camera On Main Process")
        sys.exit(main(args.uvc, args.width, args.height))
    else:
        print("Camera On Sub Process")
        p = multiprocessing.Process(
            target=main,
            args=(args.uvc, args.width, args.height),
            daemon=True
        )
        p.start()
        p.join()

