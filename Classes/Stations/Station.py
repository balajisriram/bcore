import os

from uuid import getnode

from BCore import getBaseDirectory
from BCore.Classes.Hardware import StandardParallelPort


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
    def __init__(st, **kwargs):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        st.stationID = kwargs['stationID']
        st.stationName = kwargs['stationName']
        st.stationPath = os.path.join(
            getBaseDirectory(), 'BServerData', 'StationData',
            str(st.stationID))
        st._setupPaths()
        st.MACAddress = getnode()

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
            os.path.mkdir(st.stationPath)
