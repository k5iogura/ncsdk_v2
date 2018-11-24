# How to make multi NCS' stable with RaspberryPi-3

This Tips denote how to make NCS stable running because multi NCS' running is unstable.  

### Situation
- RaspberryPi-3 Model B+
- Raspbian Stretch
- 3 or more NCS Sticks
- MiPi Camera via CSI
- GPU Memory size is default
- cpufreq governor is "ondemand"

### Notice
If multi NCS was attatched into USB ports, **use all sticks for inference, don't sleep any sticks** to avoid unstable of system.  

### Fifo size
NCSDK v2 has many options with fifo btn NCS and RaspberryPi.  
[intel Movidius Neural Compute SDK](https://movidius.github.io/ncsdk/ncapi/ncapi2/py_api/readme.html)

**We decided fifo size is over 10 in spite of Intel default size is 2.**  

fifo size depends on number of sticks running in pararell. Important Option are bellow,    

**RO_CAPACITY:** The maximum number of elements the Fifo can hold. This is set with Graph.allocate_with_fifos() or Fifo.allocate().  

We can change fifo size by parametor of **Graph.allocate_with_fifos()**.  

```
//example to specify fifo size from Intel WebSite
input_fifo, output_fifo = graph.allocate_with_fifos(
        device, graph_buffer,
        input_fifo_type=mvncapi.FifoType.HOST_WO, 
        input_fifo_num_elem=2,
        input_fifo_data_type=mvncapi.FifoDataType.FP32,
        output_fifo_type=mvncapi.FifoType.HOST_RO, 
        output_fifo_num_elem=2,
        output_fifo_data_type=mvncapi.FifoDataType.FP32
)
```
Here **input or output _fifo_num_elem** mean **fifo size** btn NCS' and RespberryPi.  

Our code is bellow,
```
self.fifo_in, self.fifo_out = self.graph_obj.allocate_with_fifos(
  self.device,
  self.graph_data,
  input_fifo_num_elem=num_elem,
  output_fifo_num_elem=num_elem
)
```

num_elem is gevin as variable, and **our default is 10**.  

Bellow are combination list of number of Sticks and image buffer size.  

|Sticks|our experiance command line|comment|
|-:||:-|
|2|python3 cam_detector.py -N 2 -b 3 -f 10 -W 320 -H 240|Stick 2, Buffer 3|
|3|python3 cam_detector.py -N 3 -b 5 -f 20 -W 320 -H 240|stick 3, Buffer 5|

### Summary of combination FiFo size, WarmUp time and Buffer size

To run stably Warm up time is needed.  

- **insert time.sleep(Sec) at first initiation of NCS'**.  

```
for i in number of NCS:
  NCS[i].open()

for i in len(buffer):
  buffer[i] = blank image
  initiate NCS[i] with buffer[i]
  time.sleep(0.2sec)
WarmUp1(1.0sec)

while True:
  for i in len(buffer):
    buffer[i] = read image from camera
    fetch result of NCS[i]
    initiate NCS[i] with buffer[i]
    WarmUp2(sec) # sec is zero or 0.020~0.030sec
```

By this warm up time each NCS behaiver became very stable but we don't know *why*.  

### FPS depends on warm up time, fifo size, buffer size

- Result of FPS vs. something parametor via perf_det.py scripts.  
**Without** reading image from camera and cv2.imshow()

```
$ python3 perf_det.py
```

|Sticks|fifo|buffer|WarmUp1|WarmUp2| FPS|  Status|
|    -:|  -:|    -:|     -:|     -:|  -:|      :-|
|     1|   5|     3|   1200|      0| 7.5|  Stable|
|     2|  10|     3|   1400|      0|16.2|  Stable|
|     3|  20|     5|   1600|     10|19.5|unstable|
|     4|  20|     6|   1800|     30|11.6|Unstable|

WarkUp[12] : msec  
FPS    : Detections / Sec  

- Result of FPS vs. something parametor via cam_detector.py scripts.  
**With** reading image from camera and cv2.imshow().  

```
$ python3 cam_detector.py -W 320 -H 240 --fifo fifo --buffer buffer
```

|Sticks|fifo|buffer|WarmUp1|WarmUp2| FPS|  Status|
|    -:|  -:|    -:|     -:|     -:|  -:|      :-|
|     1|   5|     3|   1200|      0| 7.2|  Stable|
|     2|  10|     3|   1400|      0|14.2|  Stable|
|     3|  20|     5|   1600|      0|15.5|  Stable|
|     4|  20|     6|   1800|      0|11.5|  Stable|

WarkUp[12] : msec  
FPS    : Detections / Sec  
