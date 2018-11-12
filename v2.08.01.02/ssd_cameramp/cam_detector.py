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

    Detector = [ None for i in range(0, args.Nset) ]
    for deviceNo in range(0, args.Nset):
        Detector[deviceNo] = detector(used_limit=args.Nset)
        Detector[deviceNo].set_preproc(preprocess_image)

    imgQ     = mp.Queue(33)
    rsltQ    = mp.Queue(33)
    run_flag = mp.Value('i',1)
    e_frame  = mp.Value('i',0)
    p = mp.Process(
        target=mp_video_start,
        args=(run_flag, e_frame, cam_mode, imgQ, rsltQ),
        daemon=True)
    p.start()

    latest_result = [ 0 for i in range(0,7+7*2) ]

    start = time.perf_counter()
    num_device = Detector[0].num_device
    count = 0
    while True:
        try:
            for deviceNo in range(0, num_device):
                Detector[deviceNo].initiate(imgQ.get())

            for deviceNo in range(0, num_device):
                result = Detector[deviceNo].fetch()
                if result is not None:
                    latest_result = result
                rsltQ.put(latest_result)
        except : pass

        if run_flag.value == 1:
            if (count%33)==0:
                e_time = time.perf_counter() - start
                sys.stdout.write('\b'*26)
                sys.stdout.write("%2d-%2d-%2d:%8.3f/%8.3f"%(
                    latest_result[0],
                    imgQ.qsize(),
                    rsltQ.qsize(),
                    (Detector[0].frames/e_time),
                    (e_frame.value/e_time))
                )
                sys.stdout.flush()
        else:
            break
        count += 1

    sys.stdout.write('\n')
    for deviceNo in range(0, num_device):
        Detector[deviceNo].close()

    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

#    sys.exit(main(args))

