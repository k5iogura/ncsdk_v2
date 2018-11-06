# Report of performance about NCS x Nset with SSD_MobileNet

- RaspberryPi-3 B+ x 1 with stretch  
- NCS x **Nset** with NCSDK v2.8.1.2  
- element14 MIPI-CSI Camera  
- HDMI Display  
**Nset:**Number of Used Neural Compute Sticks  

### Result Prediction FPS against Nset

|Nset|Pred|Playback|PiCamera Size|
|-:|  -:|  -:|       -:|
| 1| 6.8|20.5|  320x240|
| 2|10.9|16.2|  320x240|
| 1| 6.6|20.1|  640x480|
| 2| 7.8|11.7|  640x480|
| 1| 4.1|12.5| 1280x720|
| 2| 6.7|10.2| 1280x720|

**Reference Notice**  
*PiCamera Size* means args h/w values to picamera.videostream.__init__ contructor   

**Condition Notice**  
- SSD_MobileNet input resolution 300x300
- OpenCV-3.x.x
- Python3.5
- NCSDK v2.8.1.2

**Future Tasks**  
- Analysis relation btn Prediction Frame rate and X-Window size
- Investigate Prediction Frame rate without video output
