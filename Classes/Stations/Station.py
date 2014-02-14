import os
import time

from uuid import getnode

from BCore import getBaseDirectory
from BCore.Classes.Hardware import StandardParallelPort

PPORT_LO = 0
PPORT_HI = 1


class Station:
    """
        STATION contains all the relevant details and interfaces to run
        trials from a particular station. This is an abstract class.
        Do not instantiate.
        stationID       : numeric ID
        stationPath     : string path to data storage location
        MACAddress      : unique mac address for the processor/ethernet
                          card. string identifier
    """
    def __init__(self, **kwargs):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        self.stationID = kwargs['stationID']
        self.stationPath = os.path.join(
            getBaseDirectory(), 'BServerData', 'StationData',
            str(self.stationID))
        if not os.path.isdir(self.stationPath):
            os.path.mkdir(self.stationPath)
        self.MACAddress = getnode()

    def initializeParallelPort(st):
        try:
            pPort = StandardParallelPort(pPortAddr=st.parallelPort['pPortAddr'])
            return (pPort)
        except:
            return (None)


class StandardVisionBehaviorStation(Station):
    """
        STANDARDVISIONBEHAVIORSTATION defines a subclass of STATION.
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
    """

    def __init__(st, **kwargs):
        super(StandardVisionBehaviorStation, st).__init__(
            stationID=kwargs['stationID'])
        st.display = kwargs['display']
        st.soundOn = kwargs['soundOn']
        st.parallelPort = kwargs['parallelPort']
        pPort = st.initializeParallelPort()
        if pPort:
            st.parallelPort['pPort'] = pPort
            st.closeAllValves()
        else:
            st.parallelPort = None

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

    def startGL(st):
        pass

    def stopGL(st):
        pass

    def getDisplaySize(st):
        pass

    def doTrials(st, bServer, numTrials):
        pass
