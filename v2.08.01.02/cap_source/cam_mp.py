import sys
import time
import cv2
import numpy
import multiprocessing as mp

def cap_source(camera=0):
    window="Video"
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print("error can not open /dev/video"+str(camera))
        return
    else:
        cap.set(cv2.CAP_PROP_FPS,30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)

    frames_count = time2 = 1
    while True:
        t1 = time.perf_counter()
        ret, image = cap.read()
        if not ret:
            break
        cv2.imshow(window, image)
        if cv2.waitKey(1) != -1:
            break
        frames_count += 1
        if frames_count >= 33:
            sys.stdout.write('\b'*8+'\b'*14)
            sys.stdout.write("%8.3f FPS(Playback)"%(frames_count/time2))
            sys.stdout.flush()
            frames_count = time2 = 0
        time2 += time.perf_counter() - t1
    print("\nfinalize process cap_source")
    cap.release()
    return

if __name__=='__main__':

    #cap_process = mp.Process(target=cap_source, args=(0,))
    cap_process = mp.Process(target=cap_source, args=("police320x240.mp4",))
    cap_start = time.time()
    cap_process.start()
    cap_process.join()

    print("appd ended")
