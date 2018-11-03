#! /usr/bin/env python3

# Copyright(c) 2017 Intel Corporation. 
# License: MIT See LICENSE file in root directory.


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
#import video_processor
import queue
from g_detector import *

# name of the opencv window
cv_window_name = "SSD Mobilenet"

# labels AKA classes.  The class IDs returned
# are the indices into this list
labels = ('background',
          'aeroplane', 'bicycle', 'bird', 'boat',
          'bottle', 'bus', 'car', 'cat', 'chair',
          'cow', 'diningtable', 'dog', 'horse',
          'motorbike', 'person', 'pottedplant',
          'sheep', 'sofa', 'train', 'tvmonitor')

# the ssd mobilenet image width and height
NETWORK_IMAGE_WIDTH = 300
NETWORK_IMAGE_HEIGHT = 300

# the minimal score for a box to be shown
min_score_percent = 60

# the resize_window arg will modify these if its specified on the commandline
resize_output = False
resize_output_width = 0
resize_output_height = 0

# read video files from this directory
input_video_path = '.'

# create a preprocessed image from the source image that complies to the
# network expectations and return it
def preprocess_image(source_image):
    resized_image = cv2.resize(source_image, (NETWORK_IMAGE_WIDTH, NETWORK_IMAGE_HEIGHT))
    
    # trasnform values from range 0-255 to range -1.0 - 1.0
    resized_image = resized_image - 127.5
    resized_image = resized_image * 0.007843
    return resized_image

# handles key presses by adjusting global thresholds etc.
# raw_key is the return value from cv2.waitkey
# returns False if program should end, or True if should continue
def handle_keys(raw_key):
    global min_score_percent
    ascii_code = raw_key & 0xFF
    if ((ascii_code == ord('q')) or (ascii_code == ord('Q'))):
        return False
    elif (ascii_code == ord('B')):
        min_score_percent += 5
        print('New minimum box percentage: ' + str(min_score_percent) + '%')
    elif (ascii_code == ord('b')):
        min_score_percent -= 5
        print('New minimum box percentage: ' + str(min_score_percent) + '%')

    return True


# overlays the boxes and labels onto the display image.
# display_image is the image on which to overlay the boxes/labels
# object_info is a list of 7 values as returned from the network
#     These 7 values describe the object found and they are:
#         0: image_id (always 0 for myriad)
#         1: class_id (this is an index into labels)
#         2: score (this is the probability for the class)
#         3: box left location within image as number between 0.0 and 1.0
#         4: box top location within image as number between 0.0 and 1.0
#         5: box right location within image as number between 0.0 and 1.0
#         6: box bottom location within image as number between 0.0 and 1.0
# returns None
def overlay_on_image(display_image, object_info):
    source_image_width = display_image.shape[1]
    source_image_height = display_image.shape[0]

    base_index = 0
    class_id = object_info[base_index + 1]
    percentage = int(object_info[base_index + 2] * 100)
    if (percentage <= min_score_percent):
        return

    label_text = labels[int(class_id)] + " (" + str(percentage) + "%)"
    box_left = int(object_info[base_index + 3] * source_image_width)
    box_top = int(object_info[base_index + 4] * source_image_height)
    box_right = int(object_info[base_index + 5] * source_image_width)
    box_bottom = int(object_info[base_index + 6] * source_image_height)

    box_color = (255, 128, 0)  # box color
    box_thickness = 2
    cv2.rectangle(display_image, (box_left, box_top), (box_right, box_bottom), box_color, box_thickness)

    scale_max = (100.0 - min_score_percent)
    scaled_prob = (percentage - min_score_percent)
    scale = scaled_prob / scale_max

    # draw the classification label string just above and to the left of the rectangle
    #label_background_color = (70, 120, 70)  # greyish green background for text
    label_background_color = (0, int(scale * 175), 75)
    label_text_color = (255, 255, 255)  # white text

    label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    label_left = box_left
    label_top = box_top - label_size[1]
    if (label_top < 1):
        label_top = 1
    label_right = label_left + label_size[0]
    label_bottom = label_top + label_size[1]
    cv2.rectangle(display_image, (label_left - 1, label_top - 1), (label_right + 1, label_bottom + 1),
                  label_background_color, -1)

    # label text above the box
    cv2.putText(display_image, label_text, (label_left, label_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_text_color, 1)

    # display text to let user know how to quit
    cv2.rectangle(display_image,(0, 0),(100, 15), (128, 128, 128), -1)
    cv2.putText(display_image, "Q to Quit", (10, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

def overlay(image_to_classify, output):
    # number of boxes returned
    num_valid_boxes = int(output[0])

    for box_index in range(num_valid_boxes):
            base_index = 7+ box_index * 7
            if (not numpy.isfinite(output[base_index]) or
                    not numpy.isfinite(output[base_index + 1]) or
                    not numpy.isfinite(output[base_index + 2]) or
                    not numpy.isfinite(output[base_index + 3]) or
                    not numpy.isfinite(output[base_index + 4]) or
                    not numpy.isfinite(output[base_index + 5]) or
                    not numpy.isfinite(output[base_index + 6])):
                # boxes with non finite (inf, nan, etc) numbers must be ignored
                continue

            x1 = max(int(output[base_index + 3] * image_to_classify.shape[0]), 0)
            y1 = max(int(output[base_index + 4] * image_to_classify.shape[1]), 0)
            x2 = min(int(output[base_index + 5] * image_to_classify.shape[0]), image_to_classify.shape[0]-1)
            y2 = min((output[base_index + 6] * image_to_classify.shape[1]), image_to_classify.shape[1]-1)

            # overlay boxes and labels on to the image
            overlay_on_image(image_to_classify, output[base_index:base_index + 7])

def draw_img(display_image):
    global resize_output, resize_output_width, resize_output_height
    if (resize_output):
        display_image = cv2.resize(display_image,
                                   (resize_output_width, resize_output_height),
                                   cv2.INTER_LINEAR)
    cv2.imshow(cv_window_name, display_image)
    raw_key = cv2.waitKey(1)
    return raw_key

def main():
    global resize_output, resize_output_width, resize_output_height

    Detector = detector(overlay)
    Detector.set_preproc(preprocess_image)

    exit_app = False
    restart  = True
    buffsize = 3
    display_image=[None for i in range(0,buffsize)]
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Not found camera /dev/video0")
        sys.exit(1)
    cam.set(cv2.CAP_PROP_FPS,30)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

    cv2.namedWindow(cv_window_name)
    cv2.moveWindow(cv_window_name, 10,  10)

    ret,img = cam.read()
    Detector.initiate(img)
    playback_count = predicts_count = 0
    playback_per_second = predicts_per_second = 0
    start_time = time.perf_counter()
    while(True):
        for i in range(0, buffsize):
            try:
                ret,display_image[i] = cam.read()
                if i >= 0: image_overlapped = Detector.finish(display_image[i])
                if i == 0: Detector.initiate(display_image[i])
                raw_key = draw_img(image_overlapped)
                if (raw_key != -1):
                    if (handle_keys(raw_key) == False):
                        Detector.finish(None)
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
            playback_per_second = playback_count / (end_time - start_time)
            predicts_per_second = predicts_count / (end_time - start_time)
            sys.stdout.write('\b'*20)
            sys.stdout.write("%8.3f/%8.3fFPS"%(predicts_per_second, playback_per_second))
            sys.stdout.flush()
            start_time = time.perf_counter()
            playback_count = predicts_count = 0

        if exit_app:
            break

    # Clean up the graph and the device
    try:
        Detector.close()
        cam.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print("all finalizeing faild",e.args)
        sys.exit(1)
    print("\nfinalizing OK playback: %.2fFPS predict: %.2fFPS"%(playback_per_second, predicts_per_second))

# main entry point for program. we'll call main() to do what needs to be done.
if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("--resize",       action="store_true",     help="resize video window")
    args.add_argument("-w", "--width" , type=int, default=640,   help="video width")
    args.add_argument("-t", "--height", type=int, default=480,   help="video height")
    args.add_argument("-c", "--cam",    type=int, default=0,     help="camera index")
    args = args.parse_args()
    if args.resize: resize_output=True
    resize_output_width = args.width
    resize_output_height= args.height

    sys.exit(main())

