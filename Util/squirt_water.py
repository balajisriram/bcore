import psychopy
from psychopy import parallel
from datetime import datetime
import time
import numpy

port = parallel.ParallelPort(address='/dev/parport0')

start_time = time.time()
for i in range(300):
    port.setData(3)
    time.sleep(0.05)
    port.setData(0)
    print(i)
    m = 9
    sd = 5
    time.sleep(numpy.abs(numpy.random.normal(loc=m,scale=sd)))

print(time.time()-start_time)
