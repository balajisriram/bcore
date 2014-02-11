import os
from uuid import getnode

from BCore import getBaseDirectory


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
            para

    """

    def __init__(self, **kwargs):
        super(StandardVisionBehaviorStation, self).__init__(
            stationID=kwargs['stationID'])



