import sys

from BCore.Classes.Stations.StandardVisionBehaviorStation \
    import StandardVisionBehaviorStation


def bootstrap(mode='init', procType='client', **kwargs):
    if mode == 'init':
        if procType == 'client':
            pass
        elif procType == 'standardVisionClient' or procType == 'std-cli':
            st = StandardVisionBehaviorStation(**kwargs)
            st.run()
        elif procType == 'server':
            pass
        elif procType == 'localServer':
            pass
    elif mode == 'run':
        st = StandardVisionBehaviorStation()

if __name__ == '__main__':
    mode = 'init'
    procType = 'client'
    initSetup = False
    stationID = 0
    stationName = 'Station0'
    display = None
    soundOn = False
    parallelPort = 'standardVisionBehaviorDefault'
    # parse input arguments and send to bootstrap
    # loop through the arguments and deal with them one at a time
    args = iter(sys.argv)
    for arg in args:
        if arg == 'bootstrap':
            # do nothing. this is the initial call to python
            pass
        elif arg == 'mode' or arg == '-mode' or arg == '--mode':
            arg = next(args)
            mode = arg
        elif arg == 'procType':
            arg = next(args)
            procType = arg
        elif arg == 'stationID':
            arg = next(args)
            stationID = int(arg)
        elif arg == 'stationName':
            arg = next(args)
            stationName = arg
        elif arg == 'display':
            arg = next(args)
            display = arg
        elif arg == 'soundOn':
            arg = next(args)
            soundOn = arg
        elif arg == 'parallelPort':
            arg = next(args)
            parallelPort = arg
