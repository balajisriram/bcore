import psychopy.parallel
from datetime import datetime
import time
import numpy as np

port = psychopy.parallel.ParallelPort(address='/dev/parport0')

start_time = time.time()
for i in range(10):
    print(port.readData())
    port.setData(3)
    time.sleep(0.05)
    port.setData(0)
    print(i)
    time.sleep(0.5)

print(time.time()-start_time)
