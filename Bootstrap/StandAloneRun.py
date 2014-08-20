#! /usr/bin/python
import sys


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
    for arg in args:
        if arg == 'SubjectID':
            SARKWArgs['SubjectID'] = next(args)
        elif arg == 'BServerPath':
            SARKWArgs['BServerPath'] = next(args)
        elif arg == 'Protocol':
            SARKWArgs['Protocol'] = next(args)

        print ((arg, '::', SARKWArgs[arg]))