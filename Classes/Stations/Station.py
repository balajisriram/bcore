import os

from uuid import getnode
from verlib import NormalizedVersion as Ver


from BCore import getBaseDirectory, getIPAddr
from BCore.Classes.Hardware.Ports import StandardParallelPort


class Station(object):
    """
        STATION contains all the relevant details and interfaces to run
        trials from a particular station. This is an abstract class.
        Do not instantiate.
        stationID       : numeric ID
        stationPath     : string path to data storage location
        MACAddress      : unique mac address for the processor/ethernet
                          card. string identifier
    """
    version = Ver('0.0.1')
    stationID = 0
    stationName = ''
    stationPath = ''
    stationLocation = []
    MACAddress = ''
    IPAddr = ''
    port = 0

    def __init__(st, **kwargs):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        st.stationID = kwargs['stationID']
        st.stationName = kwargs['stationName']
        st.stationPath = os.path.join(
            getBaseDirectory(), 'BStationData', 'StationData',
            str(st.stationID))
        st.stationLocation = kwargs['stationLocation']

        st._setupPaths()
        st.MACAddress = getnode()
        st.IPAddr = getIPAddr()
        st.port = 5005  # standard for all stations.

    def getSubject(st):
        raise NotImplementedError()

    def initializeParallelPort(st):
        try:
            pPort = StandardParallelPort(pPortAddr=st.parallelPort['pPortAddr'])
            return (pPort)
        except:
            return (None)

    def _setupPaths(st):
        if not os.path.isdir(st.stationPath):
            os.makedirs(st.stationPath)

    def load(self):
        pass

    def save(self):
        pass

    def loadStation(self):
        pass

    def saveStation(self):
        pass

    def doTrials(self, **kwargs):
        raise NotImplementedError('Run doTrials() on a subclass')