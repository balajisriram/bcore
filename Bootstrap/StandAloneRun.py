#! /usr/bin/python
import sys
import zmq

SERVER_PORT = 12345

if __name__ == '__main__':
    # set defaults for all the things that need to be sent to the bootstrap
    # function
    SARKWArgs = {
        'subject_id': 'demo1',
        'bserver_path': None,
        'protocol': None,
        }
    # parse input arguments and send to bootstrap
    # loop through the arguments and deal with them one at a time
    args = iter(sys.argv)
    added = False

    for arg in args:
        if (arg == 'subject_id') or (arg == '--subject') or (arg == '-s'):
            SARKWArgs['subject_id'] = next(args)
            added = True
        elif (arg == 'bserver_path') or (arg == '--server-path'):
            SARKWArgs['bserver_path'] = next(args)
            added = True
        elif (arg == 'protocol') or (arg == '--protocol') or (arg == '-p'):
            SARKWArgs['protocol'] = next(args)
            added = True

        if added:
            print (SARKWArgs)
            added = False

    # look for local server and collect information about the Subject being run

    # find protocol and and training step num of subject being run.

    # run doTrials on subject

    # clean up at end of trials