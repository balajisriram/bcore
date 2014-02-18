import os
from BCore import getBaseDirectory


class BServer:
    """
        BSERVER  keeps track of all the stations that it commands,
        which subjects are allowed in which station and data storage locations.
            serverID            : string Identifier
            serverDataPath      : allowed data storage location
            stations            : list of stations
            subjects            : list of subjects
            assignments         : dictionary with keys being subjectID
                                and values being list of stationIDs
            revisionControl     : dictionary with access to details about
                                the repository
    """

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            # use standard location for path
            self = os.path.join(
                getBaseDirectory(), 'BServerData', 'database')
        elif len(kwargs) == 1 and 'BServerPath' in kwargs:
            pass
            #self = load
        if (
            len(kwargs) > 2) or (
                'serverID' not in kwargs) or (
                    'serverDataPath' not in kwargs):
            raise ValueError(
                'No more than 2 arguments to BServer\
                (''serverID'' and ''serverDataPath'') for initialization')
        self.version = '0.0.1'  # Feb 5, 2014
        self.serverID = kwargs['serverID']
        self.serverDataPath = kwargs['serverDataPath']
        self.log = []
        self.stations = []
        self.subjects = []
        self.assignments = {}
        self.database = []

    def _setupPaths(self):
        # create 'BServerData'
        os.path.mkdir(os.path.join(getBaseDirectory, 'BServerData'))
        # create 'ServerData','Stations','PermanentTrialRecordStore' in
        # BServerData
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'ServerData'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'StationData'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData'))
        # create 'replacedDBs' in 'ServerData'
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'ServerData', 'replacedDBs'))
        # create 'Full' and 'Compiled' in 'TrialData'
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData', 'Full'))
        os.path.mkdir(os.path.join(
            getBaseDirectory, 'BServerData', 'TrialData', 'Compiled'))

    def addStation(self, newStation):
        if newStation.stationID in self.getStationIDs():
            raise ValueError('Station IDs have to be unique')
        self.stations.append(newStation)

    def addSubject(self, newSubject, newAssignment):
        if newSubject in self.subjects:
            raise ValueError('Cannot add replica of subjects to BServer')
        if not(any(newAssignment in self.getStationIDs())):
            raise ValueError('Cannot add new subject to non existent stations')
        self.subjects.append(newSubject)
        self.assignment[newSubject.subjectID] = newAssignment

    def changeAssignment(self, subject, newAssignment):
        if subject not in self.subjects:
            raise ValueError('Cannot change assignment on a subject \
            that is not on Bserver')
        if not(any(newAssignment in self.getStationIDs())):
            raise ValueError('Cannot assign subject to non existent stations')
        self.assignment[subject.subjectID] = newAssignment

    def getStationIDs(self):
        stationIDs = []
        for station in self.stations:
            stationIDs.append(station.stationID)
        return stationIDs

    def getSubjectIDs(self):
        subjectIDs = []
        for subject in self.subjects:
            subjectIDs.append(subject.subjectID)
        return subjectIDs

if __name__ == "__main__":
    print("here")
