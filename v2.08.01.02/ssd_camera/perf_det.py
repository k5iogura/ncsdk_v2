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
from video_objects import *

cv_window_name = "Performance test NCS"

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

def main(args):
    global resize_output, resize_output_width, resize_output_height

    buffsize = 3

    Detector = [ None for i in range(0,buffsize) ]
    for i in range(0,buffsize):
        Detector[i] = detector(used_limit=args.Nset)

    exit_app = False

    cv2.namedWindow(cv_window_name)
    cv2.moveWindow(cv_window_name, 600,  200)

    blank = numpy.zeros(3*300*300).astype(numpy.float32).reshape((300,300,3)) # for performance test image

    for i in range(0,buffsize):
        img = blank
        Detector[i].initiate(img)
        draw_img(blank)

    playback_count = 0
    playback_per_second = predicts_per_second = 0
    display_image=[blank for i in range(0,buffsize)]
    start_time = time.perf_counter()
    start_frames = Detector[0].frames
    while(True):
        for i in range(0, buffsize):
            try:
                display_image[i] = blank
                image_overlapped = Detector[i].finish(None)
                Detector[i].initiate(display_image[i])
                playback_count += 1
            except Exception as e:
                print("Any Exception found:",e.args)
                exit_app = True
                break
        try:
            if (playback_count % 33) == 0:
                end_time = time.perf_counter()
                end_frames = Detector[0].frames
                playback_per_second = playback_count / (end_time - start_time)
                predicts_per_second = (end_frames - start_frames) / (end_time - start_time)
                sys.stdout.write('\b'*(20+13))
                sys.stdout.write("%8.3fFPS(%8.3fSPF)"%(predicts_per_second, 1.0/predicts_per_second))
                sys.stdout.flush()
                if cv2.waitKey(1) != -1: exit_app = True
            if exit_app: break
        except : break
        if exit_app: break

    # Clean up the graph and the device
    try:
        for i in range(0, buffsize):
            Detector[i].finish(None)
            Detector[i].close()
        cv2.destroyAllWindows()
    except : pass
    print("\nfinalizing OK predict: %.2fFPS"%(predicts_per_second))

if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("-W", "--width" ,  type=int, default=640,  help="video width")
    args.add_argument("-H", "--height",  type=int, default=480,  help="video height")
    args.add_argument("-r", "--resize",  action="store_true",    help="resize window")
    args.add_argument("-u", "--uvc",     action="store_true",    help="Use UVC")
    args.add_argument("-N", "--Nset",    type=int, default=10,   help="limit of Using Nset def=10")
    args = args.parse_args()
    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

    sys.exit(main(args))

