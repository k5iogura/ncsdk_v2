# Report of performance about NCS x Nset with SSD_MobileNet

- RaspberryPi-3 B+ x 1 with stretch  
- NCS x **Nset** with NCSDK v2.8.1.2  
- element14 MIPI-CSI Camera  
- HDMI Display  
**Nset:** Number of Used Neural Compute Sticks  

### Result Prediction FPS against Nset

***
**Abstruction of Pararell Behavier of 2set NCS**  
________________________________________________________________________\ Time

|NCS|Finish|Initiate|Finish|Initiate|Finish|Initiate|Finish|Initiate|...|
|-:|-:|-:|-:|-:|-:|-:|-:|-:|:-:|
|1|O|O|-|-|O|O|-|-|...|
|2|-|-|O|O|-|-|O|O|...|

O:Operation of Finish or Initiate for NCS  
-: Target NCS is Busy  
Finish Operation : read_elem()  
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

**Reference Notice**  
*PiCamera Size* means args h/w values to picamera.videostream.__init__ contructor.   
*X-Window* means Rendering Window size.  

**Condition Notice**  
- SSD_MobileNet input resolution 300x300
- OpenCV-3.x.x
- Python3.5
- NCSDK v2.8.1.2

