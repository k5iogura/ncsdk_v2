<img src="./files/movidius.png" alt="movidius" width="250"/>

# Setup NCS on RaspberryPI-3 Model B+

***Requirement***

RaspberryPI-3 Model B or B+  
Linux-PC  

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
ssh pi@192.168.11.18
```
Here, default ID/Password is **pi/raspberry**

**Upgrade and setup Ubuntu 16.04 environment for NCSDK**  
```
# apt update
# apt upgrade
# pip3 install opencv-python opencv-contrib-python
# apt get libusb-1.0-0 libusb-1.0-0-dev cmake
```
**Download NCSDK Version.2**
```
$ git clone https://github.com/k5iogura/ncsdk_v2
```
**Install NCSDK**
```
$ cd ncsdk_v2
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
