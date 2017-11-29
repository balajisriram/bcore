#! /usr/bin/python
import sys
import zmq

SERVER_PORT = 12345

if __name__ == '__main__':
    # set defaults for all the things that need to be sent to the bootstrap
    # function
    SARKWArgs = {
        'SubjectID': 'demo1',
        'BServerPath': None,
        'Protocol': None,
        }
    # parse input arguments and send to bootstrap
    # loop through the arguments and deal with them one at a time
    args = iter(sys.argv)
    added = False

    for arg in args:
        if (arg == 'SubjectID') or (arg == '--subject') or (arg == '-s'):
            SARKWArgs['SubjectID'] = next(args)
            added = True
        elif (arg == 'BServerPath') or (arg == '--server-path'):
            SARKWArgs['BServerPath'] = next(args)
            added = True
        elif (arg == 'Protocol') or (arg == '--protocol') or (arg == '-p'):
            SARKWArgs['Protocol'] = next(args)
            added = True

        if added:
            print (SARKWArgs)
            added = False

    # look for local server and collect information about the Subject being run

    # find protocol and and training step num of subject being run.

    # run doTrials on subject

    # clean up at end of trials