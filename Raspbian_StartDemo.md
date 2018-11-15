### How to start Demo at next of starting X-Window

Add bellow the end of file **/home/pi/.config/lxsession/LXDE-pi/autostart**  

@/home/pi/sss


```
export DISPLAY=:0
xhost +
cd /home/pi/movidius/ncsdk_v2/v2.8.1.2/ssd_camera/
python3 ssd_camera.py
```

Finaly reboot and check

