#! /usr/bin/python
"""
STANDALONERUN is the usual entry point into BCore psychophysics functionality.

StandAloneRun
     -s, --subject    subject_id
	 --server-path    server path to BServer
	 -p, --protocol   protocol object. See ../User folder for example protocols
"""
import sys
import os
from .. import get_base_directory, get_ip_addr
from ..Classes.ClientAndServer.BServer import BServerLocal
from ..Classes.Protocol import DemoProtocol
from ..Classes.SessionManager import NoTimeOff
from ..Classes.Subject import DefaultVirtual

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

SERVER_PORT = 12345

def stand_alone_run(subject_id = 'demo1', bserver_path = None, protocol = DemoProtocol):
    # look for local server and collect information about the Subject being run
    b_server = BServerLocal.load_server(bserver_path) # load the server from path
    if subject_id not in b_server.get_subject_ids():
        raise RuntimeWarning('subect % wasn''t found in server. Adding...\n',subject_id)
        sub = DefaultVirtual()
        prot = DemoProtocol()
        sub.add_protocol(prot)
        sess = NoTimeOff()
        sub.add_session_manager(sess)
	
    # find protocol and and training step num of subject being run.
    
    # run doTrials on subject

    # clean up at end of trials


if __name__ == '__main__':
    # set defaults for all the things that need to be sent to the bootstrap
    # function
    SARKWArgs = {
        'subject_id': 'demo1',
        'bserver_path': None,
        'protocol': DemoProtocol,
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

