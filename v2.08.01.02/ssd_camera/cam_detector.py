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
from video_objects import *

def overlay(source_image, result):

    if result is None:
        draw_img(source_image)
        return

    top1_idx = 0
    top1_per = 0
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

        percentage = result[offset_box+2]
        labelindex = int(result[offset_box+1])
        if percentage > top1_per:
            top1_per = percentage
            top1_idx = labelindex

    if top1_per > 0.6:
        info = "%5.1f%% %s"%(100.0*top1_per, labels[labelindex])
        spaceH = int(source_image.shape[0]*0.90)
        spaceW = int(source_image.shape[1]*0.01)
        fontSz = source_image.shape[1]/320
        if fontSz < 1.0: B=1
        else:            B=2
        cv2.putText( source_image, info, (spaceW,spaceH), cv2.FONT_HERSHEY_SIMPLEX, fontSz, (128,255,255), B, cv2.LINE_AA)

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
        Detector[i] = detector(callback_func=overlay,used_limit=args.Nset)
        Detector[i].set_preproc(preprocess_image)

    exit_app = False
    which_source = lambda x: 'UVC' if x else 'PiCamera'
    cam = video_source(which_source(args.uvc), w=args.width, h=args.height).start()

    cv2.namedWindow(cv_window_name)
    cv2.moveWindow( cv_window_name, 600,  200)

    for i in range(0,buffsize):
        img = cam.read()
        Detector[i].initiate(img)

    playback_count = predicts_count = 0
    playback_per_second = predicts_per_second = 0
    display_image=[None for i in range(0,buffsize)]
    start_time = time.perf_counter()
    start_frames = Detector[0].frames
    while(True):
        for i in range(0, buffsize):
            try:
                display_image[i] = cam.read()
        #        image_overlapped = Detector[i].finish(display_image[i]) # fetch and overlap version
                output = Detector[i].fetch()
                Detector[i].initiate(display_image[i])
                image = Detector[i].apply_callback(display_image[i], output)
                image_overlapped = Detector[i].apply_postproc(image)
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
        try:
            if (playback_count % 33) == 0:
                end_time = time.perf_counter()
                end_frames = Detector[0].frames
                playback_per_second = playback_count / (end_time - start_time)
                predicts_per_second = (end_frames - start_frames) / (end_time - start_time)
                sys.stdout.write('\b'*20)
                sys.stdout.write("%8.3f/%8.3fFPS"%(predicts_per_second, playback_per_second))
                sys.stdout.flush()

            if exit_app:
                break
        except : break

    # Clean up the graph and the device
    try:
        for i in range(0, buffsize):
            Detector[i].close()
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
    args.add_argument("-N", "--Nset",    type=int, default=10,   help="limit of Using Nset def=10")
    args = args.parse_args()
    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

    sys.exit(main(args))

