import numpy as np
import scipy.misc

import psychopy.visual
import psychopy.event

win = psychopy.visual.Window(size=[400,400],fullscr=False,units="pix")

rand_img1 = np.random.binomial(1,0.5,size=(400,400))
rand_carrier = np.random.randn(2,2)
rand_img2 = psychopy.visual.filters.makeGrating(400,ori=45,cycles=20,phase=0.)
rand_img3 = psychopy.visual.EnvelopeGrating(win,carrier=rand_carrier,envelope='sin',mask='gauss',ori=45,envori=-45,sf=0.03,envsf=0.01,size=300,contrast=0.5,moddepth=1.,pos = [-0.5,-0.5],interpolate=0)
rand_img = rand_img1+0.25*rand_img2

rand_img = rand_img - np.mean(rand_img)
rand_img = rand_img / np.std(rand_img)
rand_img = np.flipud(rand_img*2.0 - 1.0)

#img = psychopy.visual.ImageStim(win=win,image=rand_img,units="pix",size=rand_img.shape)

img_freq = np.fft.fft2(rand_img) # convert to frequency domain
img_amp = np.fft.fftshift(np.abs(img_freq)) # calculate amplitude spectrum
img_amp_disp = np.log(img_amp + 0.0001) # for display, take the logarithm
img_amp_disp = (((img_amp_disp - np.min(img_amp_disp))*2)/np.ptp(img_amp_disp)) - 1 # rescale to -1:+1 for display

img = psychopy.visual.ImageStim(win=win,image=rand_img,units="pix",size=rand_img.shape)
img2 = psychopy.visual.ImageStim(win=win,image=img_amp_disp,units="pix",size=rand_img.shape)
img.draw()
win.flip()
psychopy.event.waitKeys()
img2.draw()
win.flip()
psychopy.event.waitKeys()
rand_img3.draw()
win.flip()
psychopy.event.waitKeys()

win.close()

print("Mean::",np.mean(rand_img),np.std(rand_img))
