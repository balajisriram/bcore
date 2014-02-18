import sys


def bootstrap(mode='client', stationID=0, stationName='Station0', display=None, soundOn=False, parallelPort=None):
    if mode == 'client':
        pass
    elif mode == 'standardVisionClient':
        st = StandardVisionBehaviorStation(stationID=stationID,
                stationName=stationName 
                display=display, 
                soundOn=soundOn, 
                parallelPort='standardVisionBehaviorDefault')
        st.run()
    elif mode == 'server':
        pass
    else
        raise ValueError('')

if __name__ == '__main__':
    # parse input arguments and send to bootstrap
    # loop through the arguments and deal with them one at a time
    
    
    