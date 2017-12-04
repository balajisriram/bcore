import os

from uuid import getnode
from verlib import NormalizedVersion as Ver


from ... import get_base_directory, get_ip_addr


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
    station_id = 0
    station_name = ''
    station_path = ''
    station_location = []
    mac_address = ''
    ip_address = ''
    port = 0

    def __init__(self, station_id= 0, station_name='Station0', station_location=(0,0,0)):
        """ Use Station as an abstract class - do not allow setting of
        anything except the basic details"""
        self.station_id = station_id
        self.station_name = station_name
        self.station_path = os.path.join(
            get_base_directory(), 'BStationData', 'StationData',
            str(self.station_id))
        self.station_location = station_location

        self._setup_paths()
        self.mac_address = getnode()
        self.ip_address = get_ip_addr()
        self.port = 5005  # standard for all stations.

    def get_subject(self):
        raise NotImplementedError()

    def _setup_paths(self):
        if not os.path.isdir(self.station_path):
            os.makedirs(self.station_path)

    def load(self):
        pass

    def save(self):
        pass

    def load_station(self):
        pass

    def save_station(self):
        pass

    def do_trials(self, **kwargs):
        raise NotImplementedError('Run doTrials() on a subclass')