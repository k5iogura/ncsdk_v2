# On RaspberryPI-3 how to setup WiFi

## RaspberryPI-3 from Factory has WiFi setup?

- **prepare**  
    RaspberryPI-3 with streach raspbian  
    Other PC can connect RaspberryPI-3 via ssh(need empty file **/boot/ssh**)  
    Wired router connect internet  
    Wireless Access Point ESSID and Passphrase  

- **Search RaspberryPI IP Address on other PC in your local network**  
    Connect RaspberryPI to your router via **Wired LAN**  
    Use arp-scan command **on Other PC**  
```
    # arp-scan -l --interface eth0
    192.168.11.18	b8:27:eb:1b:df:b5	Raspberry Pi Foundation
```
Find out "Raspberry" and login it via ssh (**pi/raspberry** is default)  
```
$ ssh pi@192.168.11.18
// Look at login message
...
Wi-Fi is disabled because the country is not set.
raspberry@pi $
```
Due to above message when factory out RaspberryPI-3B+ **WiFi is disable setting**.  

- **Scan Access Point near you to connect**  
Search AP on other PC or RaspberryPI console
```
$ sudo iwlist wlan0 scan | grep ESSID
                    ESSID:"**************"
                    ESSID:"**************"
                    ....
```  
Found many AP near here:-) Select your known AP in the ESSID list.  

- **Start wpa_supplicant@wlan0.service via systemctl**  
RaspberryPI-3 is controlling WiFi as **wpa_supplicant@wlan0.service**.  
**At first** start wpa_supplicant@wlan.service to communicate raspi-config and services.  
```
$ sudo systemctl status wpa_supplicant@wlan0.service
● wpa_supplicant@wlan0.service - WPA supplicant daemon (interface-specific versi
   Loaded: loaded (/lib/systemd/system/wpa_supplicant@.service; disabled; vendor
   Active: inactive (dead)
# systemctl enable wpa_supplicant@wlan0.service
Created symlink /etc/systemd/system/multi-user.target.wants/wpa_supplicant@wlan0.service
→/lib/systemd/system/wpa_supplicant@.service.
# systemctl start wpa_supplicant@wlan0.service
# reboot
```
Look at login message, message don't show "Wi-Fi is disable".  

- **Create /etc/wpa_supplicant-wlan0.conf as WEP Client**   
**At next** create file including network setup, essid, passphrase.  
This sample is for WEP AP.  WEP passphrase is set plain text as wep_key0=.  
If you use WPA-PSK then create passphrase by bellow,
```
# wpa_supplicant <ESSID> <PLAIN TEXT PASSWORD> >>/etc/wpa_supplicant/wpa_supplicant-wlan0.conf
```
```
// create wpa_supplicant-wlan0.conf as WEP access
# vi /etc/wpa_supplicat/wpa_supplicant-wlan0.conf
# cat /etc/wpa_supplicant/wpa_supplicant-wlan0.conf 
country=JP
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
// Case of WEP
network={
    ssid="************"
    key_mgmt=NONE
    wep_key0="******"
}
// Case of WPA2-PSK
network={
    ssid="************"
    scan_ssid=1       // if stelse 1 else 0
    key_mgmt=WPA-PSK
    pairwise=CCMP     // mean AES
    group=CCMP        // mean AES
    auth_alg=OPEN     // magic word
    psk=****make this by wpa_passphrase <ESSID> <WORD> command*****
}
# reboot
```
- **Check wlan0 On RaspberryPI-3**
```
$ iwconfig
eth0      no wireless extensions.
lo        no wireless extensions.
wlan0     IEEE 802.11  ESSID:"************"  
          Mode:Managed  Frequency:2.462 GHz  Access Point: **:**:02:7D:79:81  
          Bit Rate=24 Mb/s   Tx-Power=31 dBm   
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
          Link Quality=70/70  Signal level=-25 dBm  
          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0
          Tx excessive retries:4  Invalid misc:0   Missed beacon:0
$ ifconfig wlan0
wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.11.19  netmask 255.255.255.0  broadcast 192.168.11.255
        inet6 ****::****:a437:43e5:c274  prefixlen 64  scopeid 0x20<link>
        ether **:**:eb:1b:df:b5  txqueuelen 1000  (Ethernet)
        RX packets 15  bytes 2843 (2.7 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 32  bytes 5230 (5.1 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
wireless adaptor "wlan0" setup done. WiFi-AP deploys IP-Address to RaspberryPI-3 as DHCP server.  

- **Check scanning RaspberryPI from Other PC in locak network**  
```
arp-scan -l --interface enp3s0
[sudo] ogura のパスワード:
Interface: enp3s0, datalink type: EN10MB (Ethernet)
Starting arp-scan 1.9.2 with 256 hosts (http://www.nta-monitor.com/
    tools-resources/security-tools/arp-scan/)
...
192.168.11.18	b8:27:eb:4e:8a:e0	Raspberry Pi Foundation
192.168.11.19	b8:27:eb:4e:8a:e0	Raspberry Pi Foundation
192.168.11.19	b8:27:eb:1b:df:b5	Raspberry Pi Foundation (DUP: 2)
192.168.11.19	b8:27:eb:1b:df:b5	Raspberry Pi Foundation (DUP: 3)
8 packets received by filter, 0 packets dropped by kernel
Ending arp-scan 1.9.2: 256 hosts scanned in 2.282 seconds
(112.18 hosts/sec). 8 responded
```
Found RaspberryPI as 192.168.11.19 (as 3 items).  

- **Check to connect RaspberryPI from other PC via WiFi**  
Disconnect Wired-LAN Cable and connect RaspberryPI via WiFi.  
```
$ ssh pi@192.168.11.19
pi@192.168.11.19's password: 
Linux raspberrypi 4.14.71-v7+ #1145 SMP Fri Sep 21 15:38:35 BST 2018 armv7l
The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.
Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sat Nov  3 02:46:54 2018 from 192.168.11.10
SSH is enabled and the default password for the 'pi' user has not been changed.
This is a security risk - please login as the 'pi' user and type 'passwd' to set a new password.
```
Here, ID/Password is pi/raspberry default too.  

### This is the end of story abount connection setup with RaspberryPI-3 via WiFi to other PC.  
Nov.02.2018  
