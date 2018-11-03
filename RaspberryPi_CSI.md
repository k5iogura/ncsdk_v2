# CSI Camera Setup on RaspberryPI-3

## *prepare*  
- RaspberryPI-3 Model B or B++  
  Install raspbian stretch.  
  Setup network connection or HDMI Display, keyboard and mouse.  
  
- element14 CSI Camera  

## Attatch element14 on RaspberryPI-3 board  

![](files/raspi+csi01.jpg)  
![](files/raspi+csi02.jpg)  

## Check from RaspberryPI-3 console  

```
# raspi-config
Interfaceing Options -> Camera -> 
  Would you like the camera interface to be enabled?
  Yes -> OK
  Reboot? -> Yes
$ vcgencmd get_camera
supported=1 detected=1
```
supported: means that raspi-config support csi camera  
detected : means raspi detected csi camera

If ether supported nor detected not 1 then failed csi camera support.  

## Still shut check

```
// take still
$ raspistill -o photo1.jpg
$ eog photo1.jpg
// take movie
$ raspivid -o video.h264 -t 5000
// playback
$ omxplayer video.h264
```