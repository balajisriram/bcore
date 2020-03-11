import os
import time
import json_tricks as json
import shutil
import copy
import zmq

from verlib import NormalizedVersion as Ver
from BCore import get_base_directory, get_ip_addr, get_time_stamp

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class BServer(object):
    """
        BSERVER  keeps track of all the stations that it commands,
        which subjects are allowed in which station and data storage locations.
            version             : string identifier
            serverID            : string Identifier
            serverName          : string identifier
            serverDataPath      : allowed data storage location
            serverIP            : IPV4 value
            creation_time       : time.time()
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
    """
    version = Ver('0.0.1')  # Feb 5, 2014
    server_id = ''
    server_name = ''
    server_ip = ''
    creation_time = None
    stations = []
    subjects = []
    assignments = dict()
    server_connection = []
    station_connections = []
    
    def __init__(self, **kwargs):
        pass
        
    def create_server(self, **kwargs):
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
            self.server_connection = []
            self.station_connections = {}
            self.save_server()

    def __repr__(self):
        return "BServer with id:%s, name:%s, created on:%s)" % (self.server_id, self.server_name, time.strftime("%b-%d-%Y", self.creation_time))

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
        dbLoc = os.path.join(get_base_directory(), 'BCoreData', 'ServerData', 'db.BServer')
        if os.path.isfile(dbLoc):
            with open(dbLoc, 'rb') as f:
                server = json.load(f)
            print('BServer loaded')
        else:
            raise RuntimeError('db.Server not found. Ensure it exists before calling loadServer')
        return server

    def save(self):
        """
            Alias for server.saveServer
        """
        self.save_server()

    def save_server(self):
        srcDir = os.path.join(get_base_directory(), 'BCoreData', 'ServerData')
        desDir = os.path.join(get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs')

        if not os.path.isdir(self.server_data_path):
            # assume that these are never made alone...
            self._setup_paths()

        if os.path.isfile(os.path.join(srcDir, 'db.BServer')):  # old db exists
            print(('Old db.Bserver found. moving to backup'))
            old = BServer()  # standardLoad to old
            des_name = 'db_' + get_time_stamp(old.creation_time) + '.BServer'
            shutil.copyfile(os.path.join(srcDir, 'db.BServer'),  os.path.join(desDir, des_name))
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
            get_base_directory(), 'BCoreData', 'SubjectData'))
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'ChangeParams'))
        # create 'replacedDBs' in 'ServerData'
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs'))
        # create 'Full' and 'Compiled' in 'SubjectData'
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'SubjectData', 'SessionRecords'))
        os.mkdir(os.path.join(
            get_base_directory(), 'BCoreData', 'SubjectData', 'CompiledTrialRecords'))

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


class BServerLocal(object):
    """
        BSERVERLOCAL  is a BServer which defaults to using *localhost*,
        which subjects are allowed in which station and data storage locations.
            serverID            : string Identifier
            serverDataPath      : path set by the object automatically
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
    """

    def __init__(self):
        self.server_id = 0
        self.server_data_path = os.path.join(get_base_directory(), 'BCoreData', 'ServerData')
        self.server_ip = 'http://localhost'
        self.creation_time = time.time()
        self.stations = []
        self.subjects = []
        self.assignments = {}

        print("BSERVER:BSERVERLOCAL:__INIT__:Initialized new BServerLocal object")

    def __repr__(self):
        return "BServerLocal with id:%s, name:%s, created on:%s)" % (self.server_id, self.server_name, time.strftime("%b-%d-%Y", self.creation_time))

    @staticmethod
    def load():
        """
            Alias for BServerLocal.load_server
        """
        return BServerLocal.load_server()

    @staticmethod
    def load_server(path = None):
        # if path not provided, use standard location for path,
        # make sure to never modify server here:
        if not path:
            dbLoc = os.path.join(
                get_base_directory(), 'BCoreData', 'ServerData', 'db.BServer')
        else:
            dbLoc = path
        if os.path.isfile(dbLoc):
            with open(dbLoc, 'rb') as f:
                server = pickle.load(f)
            print("BSERVER:BSERVERLOCAL:LOAD_SERVER:Loading server")
        else:
            raise RuntimeError('db.Server not found. Ensure it exists before \
                calling loadServer')

        return server

    def save(self):
        """
            Alias for server.save_server
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
            old = BServerLocal()  # standardLoad to old
            desName = 'db_' + get_time_stamp(old.creation_time) + '.BServer'
            shutil.copyfile(
                os.path.join(srcDir, 'db.BServer'),  # source
                os.path.join(desDir, desName)  # destination
                )
            print("BSERVER:BSERVERLOCAL:SAVE_SERVER:Moved to backup... deleting old copy")
            os.remove(os.path.join(srcDir, 'db.BServer'))

        # there might be some attributes that need to be deleted
        # delete them here before continuing
        print("BSERVER:BSERVERLOCAL:SAVE_SERVER:Cleaning and pickling object")
        cleanedBServer = copy.deepcopy(self)
        cleanedBServer.StationConnections = {}
        with open(os.path.join(srcDir, 'db.BServer'), 'wb') as f:
            pickle.dump(cleanedBServer, f)

    def load_backup(self):
        """
            Use this only if you specifically require the deletion of current
            db.BServer and replacement with an older backup. Only the latest
            back up is used.
        """
        desDir = os.path.join(
            BCore.get_base_directory(), 'BCoreData', 'ServerData')
        srcDir = os.path.join(
            BCore.get_base_directory(), 'BCoreData', 'ServerData', 'backupDBs')
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
        # load the backup and return it ## TOBEDONE

    def _setup_paths(self, force_delete=False):
        if force_delete:
            import shutil
            shutil.rmtree(os.path.join(get_base_directory(),'BCoreData'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','ServerData')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','ServerData'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','ServerData','backupDBs')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','ServerData','backupDBs'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','SubjectData')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','SubjectData'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','SubjectData','SessionRecords')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','SubjectData','SessionRecords'))

        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','SubjectData','CompiledTrialRecords')):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','SubjectData','CompiledTrialRecords'))

    def add_subject_permanent_trial_record_store(self,subject_id):
        if not os.path.exists(os.path.join(get_base_directory(),'BCoreData','SubjectData','SessionRecords',subject_id)):
            os.mkdir(os.path.join(get_base_directory(),'BCoreData','SubjectData','SessionRecords',subject_id))

    def create_base_compiled_record_file(self,subject_id):
        compiled_folder_path = os.path.join(get_base_directory(),'BCoreData','SubjectData','CompiledTrialRecords')
        compiled_file_for_subject = [f for f in os.listdir(compiled_folder_path) if subject_id in f]
        if not compiled_file_for_subject:
            cR = {}
            # Available in Station.do_trials()
            cR["session_number"] = [];cR["session_number"].append(0)
            cR["trial_number"] = [];cR["trial_number"].append(0)
            cR["station_id"] = [];cR["station_id"].append(None)
            cR["station_name"] = [];cR["station_name"].append(None)
            cR["station_version_number"] = [];cR["station_version_number"].append(None)
            cR["num_ports_in_station"] = [];cR["num_ports_in_station"].append(None)
            cR["trial_start_time"] = [];cR["trial_start_time"].append(None)
            cR["trial_stop_time"] = [];cR["trial_stop_time"].append(None)

            # Available in Subject.do_trial()
            cR["subject_id"] = [];cR["subject_id"].append(None)
            cR["subject_version_number"] = [];cR["subject_version_number"].append(None)
            cR["protocol_name"] = [];cR["protocol_name"].append(None)
            cR["protocol_version_number"] = [];cR["protocol_version_number"].append(None)
            cR["current_step"] = [];cR["current_step"].append(None)
            cR["current_step_name"] = [];cR["current_step_name"].append(None)
            cR["num_steps"] = [];cR["num_steps"].append(None)
            cR["criterion_met"] = [];cR["criterion_met"].append(None)

            # Available in TrainingStep.do_trial()
            cR["trial_manager_name"] = [];cR["trial_manager_name"].append(None)
            cR["session_manager_name"] = [];cR["session_manager_name"].append(None)
            cR["criterion_name"] = [];cR["criterion_name"].append(None)
            cR["reinforcement_manager_name"] = [];cR["reinforcement_manager_name"].append(None)
            cR["trial_manager_class"] = [];cR["trial_manager_class"].append(None)
            cR["session_manager_class"] = [];cR["session_manager_class"].append(None)
            cR["criterion_class"] = [];cR["criterion_class"].append(None)
            cR["reinforcement_manager_class"] = [];cR["reinforcement_manager_class"].append(None)
            cR["trial_manager_version_number"] = [];cR["trial_manager_version_number"].append(None)
            cR["session_manager_version_number"] = [];cR["session_manager_version_number"].append(None)
            cR["criterion_version_number"] = [];cR["criterion_version_number"].append(None)
            cR["reinforcement_manager_version_number"] = [];cR["reinforcement_manager_version_number"].append(None)
            cR["graduate"] = [];cR["graduate"].append(None)

            # Available in TrialManager.do_trial()
            cR["errored_out"] = [];cR["errored_out"].append(None)
            cR["manual_quit"] = [];cR["manual_quit"].append(None)
            cR["correct"] = [];cR["correct"].append(None)


            cR['LUT'] = []
            cR['compiled_details'] = {}
            cR_file_name = '{0}.1-0.compiled_records'.format(subject_id)
            with open(os.path.join(compiled_folder_path, cR_file_name),'wb') as f:
                pickle.dump(cR, f, pickle.HIGHEST_PROTOCOL)

    def initialize_server(force_delete=False):
        # setup the paths
        _setup_paths(force_delete)
        # setup the sql server

    def add_station(self, new_station):
        if (new_station.station_id in self.get_station_ids() or
                new_station.station_name in self.get_station_names()):
            raise ValueError('Station IDs and Station Names have to be unique')
        print("BSERVER:BSERVERLOCAL:SAVE_SERVER:Adding station")
        self.stations.append(new_station)
        # now enable station specific data
        self.save()

    def add_subject(self, new_subject):
        if new_subject in self.subjects:
            raise ValueError('Cannot add replica of subjects to BServer')
        print("BSERVER:BSERVERLOCAL:ADD_SUBJECT:Adding subject")
        self.subjects.append(new_subject)
        self.add_subject_permanent_trial_record_store(new_subject.subject_id)
        self.create_base_compiled_record_file(new_subject.subject_id)
        self.save()

    def remove_subject(self,subject_id):
        if subject_id not in self.get_subject_ids():
            raise ValueError('Cannot remove a subject not in server')
        print("BSERVER:BSERVERLOCAL:REMOVE_SUBJECT:Removing subject {0}".format(subject_id))
        temp = [x for x in self.subjects if x.subject_id != subject_id]
        removed = [x for x in self.subjects if x.subject_id == subject_id]
        removed = removed[0]
        self.subjects = temp
        print("BSERVER:BSERVERLOCAL:REMOVE_SUBJECT:Delete PermanentTrialRecords and CompiledTrialRecords manually")
        self.save()

    def change_reward(self,subject_id,val):
        if subject_id not in self.get_subject_ids():
            raise ValueError('Cannot remove a subject not in server')
        print("BSERVER:BSERVERLOCAL:CHANGE_REWARD:Changing reward for subject {0} to {1} ms.".format(subject_id,val))
        for i,subj in enumerate(self.subjects):
            if subj.subject_id==subject_id:
                subj.reward = val
                self.subjects[i] = subject
        self.save()

    def change_timeout(self,subject_id,val):
        if subject_id not in self.get_subject_ids():
            raise ValueError('Cannot remove a subject not in server')
        print("BSERVER:BSERVERLOCAL:CHANGE_REWARD:Changing timeout for subject {0} to {1} ms.".format(subject_id,val))
        for i,subj in enumerate(self.subjects):
            if subj.subject_id==subject_id:
                subj.timeout = val
                self.subjects[i] = subject
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

    @staticmethod
    def get_standard_server_path():
        return os.path.join(get_base_directory(),'BCoreData','ServerData','dB.BServer')

if __name__ == "__main__":
    Serv=BServer()
    with open('mydata.json','w') as f:
        json.dump(Serv,f)
