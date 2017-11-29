import zmq, time, os

from verlib import NormalizedVersion as Ver


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
            revisionControl     : dictionary with access to details about
                                the repository
    """
    version = Ver('0.0.1')  # Nov 7, 2017
    serverID = ''
    serverDataPath = ''
    serverIP = ''
    creationTime = 0
    stations = []
    subjects = []
    assignments = {}
    StationConnections = {}

    def __init__(server):
        server.serverID = 0
        server.serverDataPath = os.path.join(BCore.get_base_directory(),'BCoreData','ServerData')
        server.serverIP = 'http://localhost'
        server.creationTime = time.time()


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
