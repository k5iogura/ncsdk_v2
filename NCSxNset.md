# Report of performance about NCS x Nset with SSD_MobileNet

- RaspberryPi-3 B+ x 1 with stretch  
- NCS x **Nset** with NCSDK v2.8.1.2  
- element14 MIPI-CSI Camera  
- HDMI Display  
**Nset:**Number of Used Neural Compute Sticks  

### Result Prediction FPS against Nset

|Nset|Pred|Playback|
|-:|  -:|  -:|
| 1| 7.2|20.5|
| 2|10.6|15.8|
| 3|  Na|  Na|
| 4|  Na|  Na|

**Condition Notice**  
- OpenCV-3.x.x
- Python3.5
- NCSDK v2.8.1.2
