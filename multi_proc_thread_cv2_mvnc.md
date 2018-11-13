# Feasibility for multi threading and processing of OpenCV2 and Movidius NCS 

### Check Pararell modules combination with modules cv2 or mvnc

**Condition**:  
Main Flow call cv2 or mvnc.  
Sub Flow has infinit loop to show window or to invoke NCS Stick  
Sub Flow is invoked via threading or multiprocessing pararell module

```
// Code to estimate
def mp_para():
  while True:
    //cv2 command or ncs open/close
    
threading.Thread(target=mp_para...
or
multiprocessing.Process(target=mp_para...
```

|Method         |cv2|mvnc|
|:-:            |:-:|:-: |
|threading      | X |  O |
|multiprocessing| O |  X |
|MainThread     | O |  O |

X cv2 : occurrence of freezing  
X mvnc: occurrence of open error exception  

