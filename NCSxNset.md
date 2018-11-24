# Result of performance test about NCS x Nset with SSD_MobileNet

## [How to make multi NCS stable](HowToMakeNCSStable.md)

- RaspberryPi-3 B+ x 1 with stretch  
- NCS x **Nset** with NCSDK v2.8.1.2  
- element14 MIPI-CSI Camera  
- HDMI Display  
**Nset:** Number of Used Neural Compute Sticks  

### Result Prediction FPS against Nset

***
**Abstruction of Pararell Behavier of 2 NCS set**  

|NCS|fetch|Initiate|draw|fetch|Initiate|draw|fetch|Initiate|...|
| -:| :-: |  :-:   | :-:| :-: |  :-:   | :-:| :-: |  :-:   |:-:|
|1  |    O|       O|   O|    -|       -|   -|    O|       O|...|
|2  |    -|       -|   -|    O|       O|   O|    -|       -|...|

______________________________________________________________\ Time

O:Operation of Finish or Initiate for NCS  
-: Target NCS is Busy  
Fetch Operation : read_elem()  
Initiate Operation: queue_inference_with_fifo_elm()  
***  

**FPS With Video Rendering By OpenCV**

|Nset|Pred|Playback|PiCamera Size|X-Window|
|-:|  -:|  -:|       -:|   :-:   |
| 1| 6.8|20.5|  320x240|  320x240|
| 2|10.9|16.2|  320x240|  320x240|
| 1| 6.6|20.1|  640x480|  640x480|
| 2| 7.9|11.9|  640x480|  640x480|
| 1| 4.2|12.6| 1280x720| 1280x720|
| 2| 6.5| 9.8| 1280x720| 1280x720|

**FPS Without Video Rendering**  
Video Playback is skipped. Only pararell prediction result bellow.  

|Nset|Pred|Playback|PiCamera Size|X-Window|
|-:|  -:|  -:|       -:|:-:|
| 1| 6.6|19.8|  320x240| - |
| 2|12.6|18.9|  320x240| - |
| 1| 6.8|20.4|  640x480| - |
| 2|12.5|18.7|  640x480| - |
| 1| 6.8|20.3| 1280x720| - |
| 2|12.9|19.3| 1280x720| - |

**FPS with perf_det.py script**  
On Virtual box Ubuntu 16.04

|Nset|Pred|SPF|PiCamera Size|
|  -:|  -:|  -:|       -:|
|    | FPS|msec|  320x240|
|   1| 8.6| 116|  320x240|
|   2|17.1|  58|  320x240|
|   3|24.1|  41|  320x240|

**Reference Notice**  
*PiCamera Size* means args h/w values to picamera.videostream.__init__ contructor.   
*X-Window* means Rendering Window size.  

**Condition Notice**  
- SSD_MobileNet input resolution 300x300
- OpenCV-3.x.x
- Python3.5
- NCSDK v2.8.1.2

