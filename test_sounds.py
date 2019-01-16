from psychopy import visual, core, event, sound #import some libraries from PsychoPy
import numpy as np


#create a window
mywin = visual.Window([800,600],monitor="testMonitor", units="deg")

#create some stimuli
grating = visual.GratingStim(win=mywin, mask='circle', size=3, pos=[-4,0], sf=3)
fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0,0], sf=0, rgb=-1)

sampleRate,secs=(44100,2)
nSamples = int(secs * sampleRate)
phase = 2*np.pi*np.linspace(0.0, 1.0, nSamples)
val = np.full_like(phase,0.)
val = 0.5*np.random.randn(1,nSamples)+0.5
val = np.matlib.repmat(val,2,1)
noise_sound = sound.Sound(val.T,hamming=True)
noise_sound.seek(0.)

p_start_sound = 0.01
p_stop_sound = 0.1
sound_started = False

#draw the stimuli and update the window
while True: #this creates a never-ending loop
    grating.setPhase(0.05, '+')#advance phase by 0.05 of a cycle
    grating.draw()
    fixation.draw()
    mywin.flip()
    
    if sound_started:
        if np.random.rand()<p_stop_sound:
            print('stopping sound')
            noise_sound.pause()
            sound_started = False
    else:
        if np.random.rand()<p_start_sound:
            print('starting sound')
            noise_sound.play()
            sound_started = True

    if len(event.getKeys())>0:
        break
    event.clearEvents()

#cleanup
mywin.close()
core.quit()