import psychopy
from psychopy import parallel
from datetime import datetime
import time
import numpy as np

port = parallel.ParallelPort(address='/dev/parport0')

port_open_times = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1]
number_times = [10,20,30,50,75,100]

for open_time in port_open_times:
    for number_time in number_times:
	    for time in range(number_time):
    	    port.setData(3)
			time.sleep(open_time)
			port.setData(0)
			time.sleep(0.25)
        print('Finished open time::',open_time, 'number_time::',number_time)
		raw_input("Press enter to continue")