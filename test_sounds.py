import psychopy 
import psychopy.core
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
import psychopy.sound
import numpy as np
import numpy.matlib as matlib
import matplotlib.pyplot as plt
from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED,
                                NOT_STARTED, FOREVER)


sampleRate,secs=(44100,2)
nSamples = int(secs * sampleRate)
phase = 2*np.pi*np.linspace(0.0, 1.0, nSamples)
val = np.full_like(phase,0.)
val = 0.5*np.random.randn(1,nSamples)+0.5
val = np.matlib.repmat(val,2,1)
try_something_else_sound = psychopy.sound.Sound(val.T,hamming=True)
try_something_else_sound.seek(0.)

for i in range(15):
    # get a random interval
    print(i)
    on_interval = 0.2+0.03*np.random.randn()
    off_interval = 1+0.03*np.random.randn()
    try_something_else_sound.play()
    t = psychopy.core.getTime()
    keep_playing = True
    while keep_playing:
        psychopy.core.wait(0.001) # wait a millisecond
        keep_playing = psychopy.core.getTime()-t<on_interval
    if try_something_else_sound.status==PLAYING:
        try_something_else_sound.pause()
    t = psychopy.core.getTime()
    while(psychopy.core.getTime()-t<off_interval): psychopy.core.wait(0.001) # wait a millisecond
    

print(psychopy.core.getTime()-t)

print('Done...')

