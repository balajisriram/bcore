import os
import time
import pickle
import shutil
import copy
import zmq

from verlib import NormalizedVersion as Ver
from ... import get_base_directory, get_ip_addr, get_time_stamp


class BServer(object):
    """
        BSERVER  keeps track of all the stations that it commands,
        which subjects are allowed in which station and data storage locations.
            version             : string identifier
            serverID            : string Identifier
            serverName          : string identifier
            serverDataPath      : allowed data storage location
            serverIP            : IPV4 value
            creationTime        : time.time()
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
    """
    version = Ver('0.0.1')  # Feb 5, 2014
    server_id = ''
    server_name = ''
    server_data_path = ''
    server_ip = ''
    creation_time = 0
    stations = []
    subjects = []
    assignments = {}
    server_connection = []
    station_connections = {}

    def __init__(self, **kwargs):
        if len(kwargs) in (0, 1):
            print('BServer.__init()::', len(kwargs),
                  ' %d args input. Loading standard Server')
            self = BServer.load_server()
            if 'requireVersion' in kwargs:
                if self.version < Ver(kwargs['requireVersion']):
                    raise ValueError('you are trying to load an old version.')
        else:
            self.server_id = kwargs['server_id']
            self.server_name = kwargs['server_name']
            self.server_data_path = os.path.join(get_base_directory(), 'BCoreData', 'ServerData')
            self.server_ip = get_ip_addr()
            self.creation_time = time.time()
            self.stations = []
            self.subjects = []
            self.assignments = {}
            self.station_connections = {}
            self.save_server()

    def run(server, **kwargs):
        # should expose the ZMQ context. and allow connections
        raise NotImplementedError()

    @staticmethod
    def load():
        """
            Alias for server.loadServer
        """
        return BServer.load_server()

    @staticmethod
    def load_server():
        # use standard location for path,
        # make sure to never modify server here:
        dbLoc = os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData', 'db.BServer')
        if os.path.isfile(dbLoc):
            with open(dbLoc, 'rb') as f:
                server = pickle.load(f)

            print('BServer loaded')
        else:
            raise RuntimeError('db.Server not found. Ensure it exists before \
                calling loadServer')
        return server

    def save(self):
        """
            Alias for server.saveServer
        """
        self.save_server()

    def save_server(self):
        srcDir = os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData')
        desDir = os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs')

        if not os.path.isdir(self.server_data_path):
            # assume that these are never made alone...
            self._setup_paths()

        if os.path.isfile(os.path.join(srcDir, 'db.BServer')):  # old db exists
            print(('Old db.Bserver found. moving to backup'))
            old = BServer()  # standardLoad to old
            des_name = 'db_' + get_time_stamp(old.creation_time) + '.BServer'
            shutil.copyfile(
                os.path.join(srcDir, 'db.BServer'),  # source
                os.path.join(desDir, des_name)  # destination
            )
            print(('Moved to backup... deleting old copy'))
            os.remove(os.path.join(srcDir, 'db.BServer'))

        # there might be some attributes that need to be deleted
        # delete them here before continuing
        print(('Cleaning and pickling object'))
        cleanedBServer = copy.deepcopy(self)
        cleanedBServer.station_connections = {}
        with open(os.path.join(srcDir, 'db.BServer'), 'wb') as f:
            pickle.dump(cleanedBServer, f)

    def load_backup(self):
        """
            Use this only if you specifically require the deletion of current
            db.BServer and replacement with an older backup. Only the latest
            back up is used.
        """
        desDir = os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData')
        srcDir = os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs')
        # delete the original database
        os.remove(os.path.join(desDir, 'db.BServer'))
        # find the latest file in the backupDBs
        newestBkup = max(os.listdir(srcDir), key=os.path.getctime)
        shutil.copyfile(
            os.path.join(srcDir, newestBkup),  # source
            os.path.join(desDir, 'db.BServer')  # destination
        )
        # delete the newest backup
        os.remove(os.path.join(srcDir, newestBkup))

    def _setup_paths(server):
        # create 'BServerData'
        os.mkdir(os.path.join(get_base_directory(), 'BCoreData'))
        # create 'ServerData','Stations','PermanentTrialRecordStore' in
        # BServerData
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData'))
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'StationData'))
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'TrialData'))
        # create 'replacedDBs' in 'ServerData'
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs'))
        # create 'Full' and 'Compiled' in 'TrialData'
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'TrialData', 'Full'))
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'TrialData', 'Compiled'))

    def add_station(self, new_station):
        if (new_station.station_id in self.get_station_ids() or
                new_station.station_name in self.get_station_names()):
            raise ValueError('Station IDs and Station Names have to be unique')
        self.stations.append(new_station)
        # now enable station specific data
        self.save()

    def add_subject(self, new_subject):
        if new_subject in self.subjects:
            raise ValueError('Cannot add replica of subjects to BServer')
        self.subjects.append(new_subject)
        self.save()

    def change_assignment(self, subject, new_assignment):
        if subject not in self.subjects:
            raise ValueError('Cannot change assignment on a subject \
            that is not on Bserver')
        if not (any(new_assignment in self.get_station_ids())):
            raise ValueError('Cannot assign subject to non existent stations')
        self.assignments[subject.subject_id] = new_assignment
        self.save()

    def get_station_ids(self):
        station_ids = []
        for station in self.stations:
            station_ids.append(station.station_id)
        return station_ids

    def get_station_names(self):
        station_names = []
        for station in self.stations:
            station_names.append(station.station_name)
        return station_names

    def get_subject_ids(self):
        subject_ids = []
        for subject in self.subjects:
            subject_ids.append(subject.subject_id)
        return subject_ids


if __name__ == "__main__":
    print("here")
