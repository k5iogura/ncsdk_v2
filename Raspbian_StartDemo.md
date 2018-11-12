## How to start Demo at immediately after starting X-Window session

To start Demo program immediately after start-up X-Session, we insert bellow command lisne at the end of file **/home/pi/.config/lxsession/LXDE-pi/autostart**  

@/home/pi/sss


```
$ cat sss
sudo sh -c "echo 0 > /sys/class/graphics/fb0/blank"
export DISPLAY=:0
xhost +
cd /home/pi/movidius/ncsdk_v2/v2.08.01.02/ssd_camera/
python3 ssd_camera.py
```

Finaly reboot and check

[reference:Auto Running Programs-GUI](http://www.raspberry-projects.com/pi/pi-operating-systems/raspbian/auto-running-programs-gui)

### Abstruct  
- To avoid systemctl problems  
  Service via systemctl caused such as ": cannot connect X session :0" error. So before start of session "xhost +" command is needed by GUI user but it is impossible. To avoid this problem use user local session file such as ~/.config/lxsession/LXDE-pi/autostart.  

- No effort /etc/rc.local on stretch  
  Raspbian stretch employ systemd mechanism providing system services. Not work legacy /etc/rc.local mechanism.  