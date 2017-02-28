import time
import os

import pygame

from BCore.Classes.Stations.Station import Station
from BCore.Classes.Hardware.Ports import TCPServerConnection
from BCore.Classes.Hardware.Ports import BehaviorClientConnection
from BCore import getBaseDirectory
from BCore.Classes.TrialManagers.TrialManager import \
    VisionBehaviorSessionRecord, VisionBehaviorTrialRecord

PPORT_LO = 0
PPORT_HI = 1


class StandardVisionBehaviorStation(Station):
    """
        STANDARDVISIONBEHAVIORSTATION(SVBS) defines a subclass of STATION.
        It defines a station with a standard display, a parallel port for i/o
        with standard pin-out settings, sounds settings which can only be
        turned on or off, three valve pins, three sensor pins
        Attributes allowed are:
            stationID        : numeric ID to be sent to STATION
            stationPath      : DO NOT SEND - STATION WILL SET IT
            display          : dictionary containing details about the
                               display unit
            soundOn          : True/False
            parallelPort     : dictionary containing details about the parallel
                               port

        For the StandardVisualBehaviorStation, with Rev 2/3 breakout boards
        ("The Bomb"), only certain ports are used and for specific purposes:
            Pin 2            :            Right Reward Valve
            Pin 3            :            Center Reward Valve
            Pin 4            :            Left Reward Valve
            Pin 5            :            LED1
            Pin 6            :            eyePuff
            Pin 7            :            LED2
            Pin 8            :            indexPulse
            Pin 9            :            framePulse
            Pin 10           :            Center Response Sensor
            Pin 12           :            Right Response Sensor
            Pin 13           :            Left Response Sensor
        While, these values are not hard coded here, use these values if you
        want your system to work :)

        Use these defaults unless you know what you are doing
        parallelPort = {}
        parallelPort['rightValve'] = 2
        parallelPort['centerValve'] = 3
        parallelPort['leftValve'] = 4
        parallelPort['valvePins'] = (2, 3, 4)
        parallelPort['centerPort'] = 10
        parallelPort['rightPort'] = 12
        parallelPort['leftPort'] = 13
        parallelPort['portPins'] = (12, 10, 13)
    """
    display = ''
    soundOn = False
    parallelPort = ''
    BServerConnection = []
    session = []

    def __init__(st, **kwargs):
        super(StandardVisionBehaviorStation, st).__init__(**kwargs)
        st.display = kwargs['display']
        st.soundOn = kwargs['soundOn']
        st.parallelPort = kwargs['parallelPort']
        pPort = st.initializeParallelPort()
        if pPort:
            st.parallelPort['pPort'] = pPort
            st.closeAllValves()
        else:
            st.parallelPort = None
        st.BServerConnection = []

    def initializeParallelPort(st):
        if st.parallelPort == 'standardVisionBehaviorDefault':
            pPort = {}
            pPort['rightValve'] = 2
            pPort['centerValve'] = 3
            pPort['leftValve'] = 4
            pPort['valvePins'] = (2, 3, 4)
            pPort['centerPort'] = 10
            pPort['rightPort'] = 12
            pPort['leftPort'] = 13
            pPort['portPins'] = (12, 10, 13)
            pPort['indexPin'] = 8
            pPort['frampPin'] = 9
            pPort['LED0'] = 5
            pPort['LED1'] = 7
            st.parallelPort = pPort
            return super(
                StandardVisionBehaviorStation, st).initializeParallelPort()
        else:
            return super(
                StandardVisionBehaviorStation, st).initializeParallelPort()

    def run(st):
        # currently just show a splash
        st.splash()
        st.connectToBServer()

    def initializeDisplay(st):
        pygame.display.init()
        pygame.display.list_modes(depth=0, flags=pygame.FULLSCREEN)

    def connectToBServer(st):
        """
            This is a somewhat complicated handshake. Initially, the
            station acts as a server exposing its IP::port to the server.
            Since the server knows this IP::port it can create a client
            connection easily. Upon connection, BServer(currently client)
            sends a connection info for a separate connection(BServer will
            reserve the space for this connection) to the station and the
            station will connect to the BServer now as a client. This way
            new stations can be added to the server without any
            station-side code modification. BServer can dynamically manage
            its resources. Along with threaded TCP server connections on
            the server side, this should provide scalable, TCP communications
            with the server
        """
        st.BServerConnection = TCPServerConnection(ipaddr=st.IPAddr,
            port=st.port)
        st.BServerConnection.start()
        BServerConnDetails = st.BServerConnection.recvData()
        # use BServerConnDetails to connect to the BServer as a client
        print('Closing connection as server...')
        st.BServerConnection.stop()
        st.BServerConnection = BehaviorClientConnection(
            ipaddr=BServerConnDetails['ipaddr'],
            port=BServerConnDetails['port'])
        print(('Starting connection as client...'))
        st.BServerConnection.start()

    def getSubject(st):
        """
            For STANDARDVISIONBEHAVIORSTATION.GETSUBJECT(), get data from
            BServer
        """
        raise NotImplementedError()

    def closeAllValves(st):
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_LO)

    def readPorts(st):
        st.parallelPort['pPort'].readPins(
            st.parallelPort['portPins'])

    def openValve(st, valve):
        st.parallelPort['pPort'].writePins(
            st.parallelPort[valve], PPORT_HI)

    def closeValve(st, valve):
        st.parallelPort['pPort'].writePins(
            st.parallelPort[valve], PPORT_LO)

    def flushValves(st, dur):
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_HI)
        time.sleep(dur)
        st.parallelPort['pPort'].writePins(
            st.parallelPort['valvePins'], PPORT_LO)

    def splash(st):
        pygame.init()
        size = width, height = 600, 400

        screen = pygame.display.set_mode(size)
        splashTex = pygame.image.load(os.path.join(
            getBaseDirectory(), 'BCore', 'Util', 'Resources', 'splash.png'))

        screen.blit(splashTex, [0, 0])
        pygame.display.flip()

        time.sleep(1)

    def getDisplaySize(st):
        pass

    def getSession(st):
        """
            Connect to BServer and request session details to be loaded
        """
        pass

    def getCompiledRecords(st):
        """
            Connect to BServer and request compiledRecords
        """
        pass

    def decache(st):
        """
            Remove session specific details. ideal for pickling
        """
        pass

    def doTrials(st, **kwargs):
        # first step in the running of trials. called directly by station
        # or through the BServer
        if __debug__:
            pass

        # find the subject
        st.getSession()
        cR = st.getCompiledRecords()

        Quit = False

        # session starts here
        sR = VisionBehaviorSessionRecord()  # make new session record

        while not Quit and not st.session.stop():
            # it loops in here every trial
            tR = VisionBehaviorTrialRecord()
            # just assign relevant details here
            tR.trialNumber = cR.trialNumber[-1] + 1
            tR.sessionNumber = st.session.sessionNumber
            tR.stationID = st.stationID
            tR.stationName = st.stationName
            tR.numPortsInStation = st.numPorts()
            tR.startTime = time.localtime()
            tR.subjectsInStation = st.subjectsInStation()
            # doTrial - only tR will be returned as its type will be changed
            tR = st.session.subject.doTrial(station=st, trialRecord=tR,
                compiledRecord=cR, quit=Quit)

            tR.stopTime = time.localtime()
            # update sessionRecord and compiledRecord
            sR.append(tR)
            cR.append(tR)


class SimpleVisionBehaviorStation(object):

    def __init__(self):
        print('Creating SimpleVisionBehaviorStation')

    def testGL(st):
        pygame.init()
        size = width, height = 600, 400
        screen = pygame.display.set_mode(size)
        splashTex = pygame.image.load(os.path.join(
            getBaseDirectory(), 'BCore', 'Util', 'Resources', 'splash.png'))
        screen.blit(splashTex, [0, 0])
        pygame.display.flip()
        time.sleep(1)

if __name__ == '__main__':
    import sys
    print((sys.version))
    # Create a new StandardVisionBehaviorStation and test it
    #st = StandardVisionBehaviorStation(stationID=0,
    #    display=None, soundOn=False, parallelPort=None)
    st = SimpleVisionBehaviorStation()
    print(('Testing the station\'s graphics'))
    st.testGL()
    time.sleep(2)