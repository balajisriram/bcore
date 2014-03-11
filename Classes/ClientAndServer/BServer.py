import os
import time
import cPickle as pickle
import shutil
import copy

from verlib import NormalizedVersion as Ver
from BCore import getBaseDirectory, getIPAddr, getTimeStamp
from BCore.Util.BehaviorServerGUI.BehaviorServerGUI import BServerApp


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
            revisionControl     : dictionary with access to details about
                                the repository
    """
    version = Ver('0.0.1')  # Feb 5, 2014
    serverID = ''
    serverDataPath = ''
    serverIP = ''
    creationTime = 0
    stations = []
    subjects = []
    assignments = {}
    StationConnections = {}

    def __init__(server, **kwargs):
        if len(kwargs) in (0, 1):
            print('BServer.__init()::', len(kwargs),
                ' %d args input. Loading standard Server')
            server = server.loadServer()
            if 'requireVersion' in kwargs:
                if server.version < Ver(kwargs['requireVersion']):
                    raise ValueError('you are trying to load an old version.')
        else:
            server.serverID = kwargs['serverID']
            server.serverName = kwargs['serverName']
            server.serverDataPath = os.path.join(
                getBaseDirectory(), 'BCoreData', 'ServerData')
            server.serverIP = getIPAddr()
            server.creationTime = time.time()
            server.stations = []
            server.subjects = []
            server.assignments = {}
            server.StationConnections = {}
            server.saveServer()

    def run(server, **kwargs):
        print(('Running server...\n'))
        if kwargs['serverGUI']:
            BServerApp(serverData=server)
            pass
        else:
            raise NotImplementedError()

    def load(server):
        """
            Alias for server.loadServer
        """
        return server.loadServer()

    def loadServer(server):
        # use standard location for path,
        # make sure to never modify server here:
        dbLoc = os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData', 'db.BServer')
        if os.path.isfile(dbLoc):
            f = open(dbLoc, 'rb')
            server = pickle.load(f)
            f.close()
            print('BServer loaded')
        else:
            raise RuntimeError('db.Server not found. Ensure it exists before \
                calling loadServer')
        return server

    def save(server):
        """
            Alias for server.saveServer
        """
        server.saveServer()

    def saveServer(server):
        srcDir = os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData')
        desDir = os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData', 'backupDBs')

        if not os.path.isdir(server.serverDataPath):
            # assume that these are never made alone...
            server._setupPaths()

        if os.path.isfile(os.path.join(srcDir, 'db.BServer')):  # old db exists
            print(('Old db.Bserver found. moving to backup'))
            old = BServer()  # standardLoad to old
            desName = 'db_' + getTimeStamp(old.creationTime) + '.BServer'
            shutil.copyfile(
                os.path.join(srcDir, 'db.BServer'),  # source
                os.path.join(desDir, desName)  # destination
                )
            print(('Moved to backup... deleting old copy'))
            os.remove(os.path.join(srcDir, 'db.BServer'))

        # there might be some attributes that need to be deleted
        # delete them here before continuing
        print(('Cleaning and pickling object'))
        cleanedBServer = copy.deepcopy(server)
        cleanedBServer.StationConnections = {}
        f = open(os.path.join(srcDir, 'db.BServer'), 'wb')
        pickle.dump(cleanedBServer, f)
        f.close()

    def loadBackup(server):
        """
            Use this only if you specifically require the deletion of current
            db.BServer and replacement with an older backup. Only the latest
            back up is used.
        """
        desDir = os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData')
        srcDir = os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData', 'backupDBs')
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

    def _setupPaths(server):
        # create 'BServerData'
        os.mkdir(os.path.join(getBaseDirectory(), 'BCoreData'))
        # create 'ServerData','Stations','PermanentTrialRecordStore' in
        # BServerData
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData'))
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'StationData'))
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'TrialData'))
        # create 'replacedDBs' in 'ServerData'
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'ServerData', 'backupDBs'))
        # create 'Full' and 'Compiled' in 'TrialData'
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'TrialData', 'Full'))
        os.mkdir(os.path.join(
            getBaseDirectory(), 'BCoreData', 'TrialData', 'Compiled'))

    def addStation(server, newStation):
        if (newStation.stationID in server.getStationIDs() or
            newStation.stationName in server.getStationNames()):
            raise ValueError('Station IDs and Station Names have to be unique')
        server.stations.append(newStation)
        # now enable station specific data
        server.save()

    def addSubject(server, newSubject):
        if newSubject in server.subjects:
            raise ValueError('Cannot add replica of subjects to BServer')
        server.subjects.append(newSubject)
        server.save()

    def changeAssignment(server, subject, newAssignment):
        if subject not in server.subjects:
            raise ValueError('Cannot change assignment on a subject \
            that is not on Bserver')
        if not(any(newAssignment in server.getStationIDs())):
            raise ValueError('Cannot assign subject to non existent stations')
        server.assignment[subject.subjectID] = newAssignment
        server.save()

    def getStationIDs(server):
        stationIDs = []
        for station in server.stations:
            stationIDs.append(station.stationID)
        return stationIDs

    def getStationNames(server):
        stationNames = []
        for station in server.stations:
            stationNames.append(station.stationName)
        return stationNames

    def getSubjectIDs(server):
        subjectIDs = []
        for subject in server.subjects:
            subjectIDs.append(subject.subjectID)
        return subjectIDs

if __name__ == "__main__":
    print("here")
