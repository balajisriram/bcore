import zmq, time, os, pickle, shutil

from verlib import NormalizedVersion as Ver
from ... import get_base_directory

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
    version = Ver('0.0.1')  # Nov 7, 2017
    server_id = ''
    server_data_path = ''
    server_ip = ''
    creation_time = 0
    stations = []
    subjects = []
    assignments = {}
    StationConnections = {}

    def __init__(self):
        self.server_id = 0
        self.server_data_path = os.path.join(BCore.get_base_directory(),'BCoreData','ServerData')
        self.server_ip = 'http://localhost'
        self.creation_time = time.time()

    @staticmethod
    def load():
        """
            Alias for BServerLocal.loadServer
        """
        return BServerLocal.load_server()

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
            old = BServerLocal()  # standardLoad to old
            desName = 'db_' + get_time_stamp(old.creationTime) + '.BServer'
            shutil.copyfile(
                os.path.join(srcDir, 'db.BServer'),  # source
                os.path.join(desDir, desName)  # destination
                )
            print(('Moved to backup... deleting old copy'))
            os.remove(os.path.join(srcDir, 'db.BServer'))

        # there might be some attributes that need to be deleted
        # delete them here before continuing
        print(('Cleaning and pickling object'))
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

    def _setup_paths(force_delete=False):
        if force_delete:
            import shutils
            shutils.rmtree(os.path.join(BCore.get_base_directory,'BCoreData'))

        if not os.path.exist(os.path.join(BCore.get_base_directory,'BCoreData')):
            os.mkdir(os.path.join(BCore.get_base_directory,'BCoreData'))

        if not os.path.exist(os.path.join(BCore.get_base_directory,'BCoreData','ServerData')):
            os.mkdir(os.path.join(BCore.get_base_directory,'BCoreData','ServerData'))

        if not os.path.exist(os.path.join(BCore.get_base_directory,'BcoreData','ServerData','Backups')):
            os.mkdir(os.path.join(BCore.get_base_directory,'BCoreData','ServerData','Backups'))


    def initialize_server(force_delete=False):
        # setup the paths
        _setup_paths(force_delete)
        # setup the sql server


if __name__ == "__main__":
    print("here")
