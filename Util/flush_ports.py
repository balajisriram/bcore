import psychopy
from psychopy import parallel
from datetime import datetime
import time
import numpy

port = parallel.ParallelPort(address='/dev/parport0')

start_time = time.time()
for i in range(10):
    port.setData(3)
    time.sleep(0.05)
    port.setData(0)
    print(i)
    time.sleep(0.5)

print(time.time()-start_time)
