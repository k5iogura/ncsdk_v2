# Make RaspberryPi-3 WiFiAP

**WiFi Access Point on RaspberryPi-3**  
This page assumpt that AP board has **2 network interfaces** of Wired EtherLAN and WiFi.  

|Interface|get IP from|Connect To|Connected from|    IP example|
|       -:|         -:|        -:|            -:|            -:|
|     eth0|     dhcpcd|  Internet|             -|192.168.137.21|
|    wlan0|     static|      eth0|   WiFi Client|      10.0.0.1|

**Supplicant WiFi Client such as RaspberryPi**  
Also assumpt that WiFI Client has a network interface like wlan0.  


|Interface|get IP from|Connect To|    Connected from|    IP example|
|       -:|         -:|        -:|                -:|            -:|
|    wlan0| AP dnsmasq|   WiFi-AP|Other WiFi Clients|      10.0.0.4|

### Stop and make disable WiFi Client if RaspberryPi-3 was WiFi Client  
If RaspberryPi-3 was running **as WiFi Client then stop it** and diable WiFi Client.  
```
//check
# systemctl status wpa_supplicant@wlan0.service
//stop and disable
# systemctl stop wpa_supplicant@wlan0.service
# systemctl disable wpa_supplicant@wlan0.service
//chech
# systemctl status wpa_supplicant@wlan0.service
systemctl status wpa_supplicant@wlan0.service
● wpa_supplicant@wlan0.service - WPA supplicant daemon (interface-specific version)
   Loaded: loaded (/lib/systemd/system/wpa_supplicant@.service; disabled;
   vendor preset: enabled)
   Active: inactive (dead)
   ...
```

### Install dnsmasq and hostapd
- **dnsmasq: providing DNS and DHCP server**  
- **hostapd: providing WiFi Access Point server**  

Install both server tools. At first **install dnsmasq package** like bellow,  
```
# apt install dnsmasq
//check
$ ls /etc/dnsmasq*
/etc/dnsmasq.conf
/etc/dnsmasq.d:
README

$ cat README 
# All files in this directory will be read by dnsmasq as 
# configuration files, except if their names end in 
# ".dpkg-dist",".dpkg-old" or ".dpkg-new"
# This can be changed by editing /etc/default/dnsmasq$ ls /etc/hostapd*

$ systemctl status dnsmasq.service
● dnsmasq.service - dnsmasq - A lightweight DHCP and caching DNS server
   Loaded: loaded (/lib/systemd/system/dnsmasq.service; enabled; 
   vendor preset: enabled)
   Active: active (running) since Sat 2018-11-10 04:54:44 GMT; 1h 7min ago
 Main PID: 1474 (dnsmasq)
   CGroup: /system.slice/dnsmasq.service
           └─1474 /usr/sbin/dnsmasq -x /run/dnsmasq/dnsmasq.pid -u 
           dnsmasq -r /run/dnsmasq/resolv.conf -7 /etc/dn

Nov 10 04:54:44 raspberrypi systemd[1]: Starting dnsmasq - A lightweight
DHCP and caching DNS server...
Nov 10 04:54:44 raspberrypi dnsmasq[1463]: dnsmasq: syntax check OK.
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: started, version 2.76 cachesize150
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: compile time options: IPv6 
                                   GNU-getopt DBus i18n IDN DHCP DHCPv6 no-Lua
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: DNS service limited to local subnets
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: reading /run/dnsmasq/resolv.conf
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: using nameserver 192.168.11.1#53
Nov 10 04:54:44 raspberrypi dnsmasq[1474]: read /etc/hosts - 5 addresses
Nov 10 04:54:44 raspberrypi dnsmasq[1475]: Too few arguments.
Nov 10 04:54:44 raspberrypi systemd[1]: Started dnsmasq - A lightweight
DHCP and caching DNS server.

```
You could see setting files and directory and could ensure that **dnsmasq.service is running**.  

At next, **install hostapd package** like bellow,
```
# apt install hostapd
//check
$ ls /etc/hostapd/
ifupdown.sh

```

### Setup DNS and DHCP server with dnsmasq package on wlan0
Set interface name, dhcp range to deploy **in /etc/dnsmasq.d/dnsmasq.conf**.  
```
interface=wlan0
dhcp-range=10.0.0.2,10.0.0.5,255.255.255.0,12h
```
RaspberryPi-3 deploy one IP-Address selected **from 10.0.0.2 to 10.0.0.5** to supplicant WiFi Client **with 12Hours** limitation via interface wlan0.  
Restart dnsmasq.service.  
```
# systemctl restart dnsmasq.service
//check
$ systemctl status dnsmasq.service -l
...
Nov 10 06:49:44 raspberrypi dnsmasq[2701]: warning: interface wlan0
                                           does not currently exist
Nov 10 06:49:44 raspberrypi dnsmasq-dhcp[2701]: DHCP, IP range 10.0.0.2 --
                                                10.0.0.5, lease time 12h
Nov 10 06:49:44 raspberrypi dnsmasq[2701]: reading /run/dnsmasq/resolv.conf
Nov 10 06:49:44 raspberrypi dnsmasq[2701]: using nameserver 192.168.11.1#53
...
```
As of now interface **"wlan0" not working**.  

### Setup WiFI AP server with hostapd package on wlan0

#### Setup hostapd

Modify **/etc/default/hostapd**  
```
DAEMON_CONF=/etc/hostapd/hostapd.conf
```

By above discription hostapd read local hostapd.conf.  

Create **/etc/hostapd/hostapd.conf** as custom setup.  

```
# vi /etc/hostapd/hostapd.conf | egrep -v '^$'
interface=wlan0
hw_mode=g
channel=9
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
wpa_passphrase=********
ssid=rpi3
ieee80211n=1
wmm_enabled=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
```
Notice that wpa_passphrase lenght. **wpa_passphrase must be 8..63 characters**.  

#### Setup interface  

**By /etc/network/interfaces.d/home.conf** fix static ip address of wlan0.  

```
allow-hotplug wlan0

iface wlan0 inet static
    address 10.0.0.1
    netmask 255.255.255.0
    network 10.0.0.0
    broadcast 10.0.0.255
```

### Disable dhcpcd of wlan0 

**By /etc/dhcpcd.conf** disable dhcp client for **wlan0**.
```
# vi /etc/dhcpcd.conf
//check
$ cat /etc/dhcpcd.conf | egrep -v '(^#|^$)'
hostname
clientid
persistent
option rapid_commit
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
option ntp_servers
option interface_mtu
require dhcp_server_identifier
slaac private
#interface wlan0
#static ip_address=10.0.0.1/24
#static routers=192.168.11.1
denyinterfaces wlan0
```

Restart dhcpcd and check
```
# systemctl restart dhcpcd.service
//check
systemctl status dhcpcd
● dhcpcd.service - dhcpcd on all interfaces
   Loaded: loaded (/lib/systemd/system/dhcpcd.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2018-11-10 10:04:30 GMT; 9min ago
  Process: 1038 ExecStop=/sbin/dhcpcd -x (code=exited, status=0/SUCCESS)
  Process: 1045 ExecStart=/usr/lib/dhcpcd5/dhcpcd -q -b (code=exited, status=0/SUCCESS)
 Main PID: 1048 (dhcpcd)
   CGroup: /system.slice/dhcpcd.service
           └─1048 /sbin/dhcpcd -q -b

Nov 10 10:04:30 raspberrypi dhcpcd[1045]: forked to background, child pid 1048
Nov 10 10:04:30 raspberrypi systemd[1]: Started dhcpcd on all interfaces.
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: DUID 00:01:00:01:23:4f:5f:0d:b8:27:eb:1b:df:b5
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: IAID eb:5d:51:a9
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: rebinding lease of 192.168.11.21
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: leased 192.168.11.21
                                                  for 172800 seconds
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: changing route to
                                                     192.168.11.0/24
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: changing default route via
                                                        192.168.11.1
Nov 10 10:04:30 raspberrypi dhcpcd[1048]: eth0: soliciting an IPv6 router
Nov 10 10:04:42 raspberrypi dhcpcd[1048]: eth0: no IPv6 Routers available
```

Check more like bellow,

```
$ ifconfig wlan0
wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.0.1  netmask 255.255.255.0  broadcast 10.0.0.255
        inet6 fe80::ba27:ebff:fe08:4fc  prefixlen 64  scopeid 0x20<link>
        ether **:**:**:08:04:fc  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 47  bytes 6378 (6.2 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

Start hostapd.  

```
# systemctl enable hostapd.service
# systemctl start hostapd.service
//check
# systemctl status hostapd.service
● hostapd.service - LSB: Advanced IEEE 802.11 management daemon
   Loaded: loaded (/etc/init.d/hostapd; generated; vendor preset: enabled)
   Active: active (running) since Sat 2018-11-10 07:52:20 GMT; 9min ago
     Docs: man:systemd-sysv-generator(8)
  Process: 1024 ExecStop=/etc/init.d/hostapd stop (code=exited, status=0/SUCCESS)
  Process: 1031 ExecStart=/etc/init.d/hostapd start (code=exited, status=0/SUCCESS)
   CGroup: /system.slice/hostapd.service
           └─1038 /usr/sbin/hostapd -B -P /run/hostapd.pid /etc/hostapd/hostapd.conf

Nov 10 07:52:20 raspberrypi systemd[1]: Starting LSB: Advanced 
                                            IEEE 802.11 management daemon.
Nov 10 07:52:20 raspberrypi hostapd[1031]: Starting advanced 
                                          IEEE 802.11 management: hostapd.
Nov 10 07:52:20 raspberrypi systemd[1]: Started LSB: Advanced 
                                            IEEE 802.11 management daemon.
```

If /etc/hostapd/hostapd.conf was **invalid then** you can see bellow,

```
Nov 10 07:47:35 raspberrypi hostapd[986]: Starting advanced 
                                       IEEE 802.11 management: hostapd failed!
```

wlan0 is setup bellow,

```
# iwconfig
eth0      no wireless extensions.
lo        no wireless extensions.
wlan0     IEEE 802.11  Mode:Master  Tx-Power=31 dBm   
          Retry short limit:7   RTS thr:off   Fragment thr:off
          Power Management:on
```

### Check default gw

As of now WiFi Client connecting AP **can not go internet** but WiFi AP can go internet.  

```
//check
$ route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
default         apdcfb027d7980  0.0.0.0         UG    202    0        0 eth0
10.0.0.0        0.0.0.0         255.255.255.0   U     0      0        0 wlan0
192.168.11.0    0.0.0.0         255.255.255.0   U     202    0        0 eth0

```

```
$ ping google.co.jp
PING google.co.jp (172.217.25.99) 56(84) bytes of data.
64 bytes from nrt13s51-in-f99.1e100.net (172.217.25.99): icmp_seq=1 ttl=53 time=21.8 ms
64 bytes from nrt13s51-in-f99.1e100.net (172.217.25.99): icmp_seq=2 ttl=53 time=22.1 ms
64 bytes from nrt13s51-in-f99.1e100.net (172.217.25.99): icmp_seq=3 ttl=53 time=28.5 ms
```