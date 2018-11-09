<img src="./files/movidius.png" alt="movidius" width="250"/>

# Setup NCS on RaspberryPI-3 Model B+

# [RaspberryPI-3 WiFi setup here](RaspberryPI_WiFi.md)
# [Using PiCamera via picamera module here](RaspberryPi_CSI.md)

## Install NCSDK v2.08.01.02
***Requirement***

RaspberryPI-3 Model B or B+  
Linux-PC with internet connection  

***On Linux PC***

- Ubuntu 16.04 base **"Strech"** download from HP and write it into SDCard  
- Create empty file on /boot  
  insert SDCard to Linux PC  
  **touch /boot/ssh** to make sshd enable on Raspbian.    

***On RaspberryPi***

- Connect LAN Port to internet-rooter with LAN Cable  
- Insert SDCard into RaspberryPi  
- Power On

***On Linux PC Again***

- Issue arp-scan command to know IP-Address of Raspberry-PI
```
# arp-scan -l --interface eth0
192.168.11.18	xx:yy:eb:4e:8a:e0	Raspberry Pi Foundation
```
- connect to RaspberryPI via ssh
```
$ ssh pi@192.168.11.18
$ uname -a
Linux raspberrypi 4.14.71-v7+ #1145 SMP Fri Sep 21 15:38:35 BST 2018 armv7l GNU/Linux
```
Here, default ID/Password is **pi/raspberry**

**Upgrade and setup Ubuntu 16.04 environment for NCSDK**  
```
# apt update
# apt upgrade
# pip3 install opencv-python opencv-contrib-python
# apt get libusb-1.0-0 libusb-1.0-0-dev cmake
```
***[Tips:ラズパイカメラを使って連続撮影＆fbiコマンドでCUI画面のフレームバッファに直接表示する方法。SSH経由でもOK！](https://iot-plus.net/make/raspi/raspistill-continuous-shooting-displays-on-cui-using-frame-buffer-with-ssh-connection/)***  
Disable **Display Blank**  
Fixing disable Display Blanking, some operation is needed,
```
# echo 0 > /sys/class/graphics/fb0/blank   # force display blank on
# echo 1 > /sys/class/graphics/fb0/blank   # force display blank off
```
[Also may need bellow](https://www.geeks3d.com/hacklab/20160108/how-to-disable-the-blank-screen-on-raspberry-pi-raspbian/),
```
# vi /etc/lightdm/lightdm.conf
[SeatDefaults]
xserver-command=X -s 0 -dpms
```
and reboot!

**Download NCSDK Version.2**
```
// As installation under Home directory,,,
$ cd
$ git clone https://github.com/k5iogura/ncsdk_v2
```
**Install NCSDK API-Mode**  
For easy checking of NCS install NCSDK API-Mode before NCSDK Full Install.
```
$ cd ncsdk_v2/api/src
$ make
$ sudo make install
```
**Check NCS**  
Insert NCS into USB Port on RaspberryPI.  
```
$ dmesg | tail
[ 2303.064806] usb 1-1.3: new high-speed USB device number 5 using dwc_otg
[ 2303.196020] usb 1-1.3: New USB device found, idVendor=03e7, idProduct=2150
[ 2303.196035] usb 1-1.3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 2303.196044] usb 1-1.3: Product: Movidius MA2X5X
[ 2303.196052] usb 1-1.3: Manufacturer: Movidius Ltd.
[ 2303.196061] usb 1-1.3: SerialNumber: 03e*****
```
Find out MA2X5X as Movidius NCS.  
**Check Device Hello**
```
$ cd ~/ncsdk_v2
$ python3 examples/apps/hello_ncs_py/hello_ncs.py 
D: [         0] ncDeviceCreate:307	ncDeviceCreate index 0
D: [         0] ncDeviceCreate:307	ncDeviceCreate index 1
D: [         0] ncDeviceOpen:523	File path /usr/local/lib/mvnc/MvNCAPI-ma2450.mvcmd
I: [         0] ncDeviceOpen:529	ncDeviceOpen() XLinkBootRemote returned success 0
I: [         0] ncDeviceOpen:567	XLinkConnect done - link Id 0
D: [         0] ncDeviceOpen:581	done
I: [         0] ncDeviceOpen:583	Booted 1.3-ma2450 -> VSC
I: [         0] getDevAttributes:382	Device attributes
I: [         0] getDevAttributes:385	Device FW version: 2.8.2450.16e
I: [         0] getDevAttributes:387	mvTensorVersion 2.8 
I: [         0] getDevAttributes:388	Maximum graphs: 10
I: [         0] getDevAttributes:389	Maximum fifos: 20
I: [         0] getDevAttributes:391	Maximum graph option class: 1
I: [         0] getDevAttributes:393	Maximum device option class: 1
I: [         0] getDevAttributes:394	Device memory capacity: 522059056
Hello NCS! Device opened normally.
I: [         0] ncDeviceClose:775	closing device
Goodbye NCS! Device closed normally.
NCS device working.
```
OK Device Open/Close.  

## UVC Camera check

**Insert UVC Camera into USB Port**  
Recognize UVC Camera to Linux
```
$ dmesg | tail
[ 3935.504543] uvcvideo: Found UVC 1.00 device <unnamed> (046d:0825)
[ 3935.519553] uvcvideo 1-1.1.3:1.0: Entity type for entity Extension 4 was not initialized!
[ 3935.519572] uvcvideo 1-1.1.3:1.0: Entity type for entity Extension 6 was not initialized!
[ 3935.519582] uvcvideo 1-1.1.3:1.0: Entity type for entity Extension 7 was not initialized!
[ 3935.519593] uvcvideo 1-1.1.3:1.0: Entity type for entity Processing 2 was not initialized!
[ 3935.519603] uvcvideo 1-1.1.3:1.0: Entity type for entity Extension 3 was not initialized!
[ 3935.519612] uvcvideo 1-1.1.3:1.0: Entity type for entity Camera 1 was not initialized!
[ 3935.519994] input: UVC Camera (046d:0825) as /devices/platform/soc/3f980000.usb/usb1/1-1/1-1.1/1-1.1.3/1-1.1.3:1.0/input/input0
[ 3935.520233] usbcore: registered new interface driver uvcvideo
[ 3935.520239] USB Video Class driver (1.1.1)
```
Find out UVC Camera  
**Check OpenCV Camera sample**  
Allow X-Window client form RaspberryPI to Linux PC X-Window server,
```
$ xhost + 192.168.11.18
192.168.11.18 being added to access control list
```
On RaspberryPI run basic camera python script,
```
// install opencv + contrib + ffmpeg +...
# apt install -y libopencv-dev libopencv-contrib-dev
# apt install -y libqtgui4 libqttest4-perl
$ export DISPLAY=192.168.11.10:0
$ python3 first_contact/cam.py
```

## [Using PiCamera via picamera module here](RaspberryPi_CSI.md)
