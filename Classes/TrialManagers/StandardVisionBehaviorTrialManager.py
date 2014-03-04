from BCore.Classes.TrialManagers.TrialManager import TrialManager
from BCore.Classes.TrialManagers.TrialManager import TrialRecord
from BCore.Classes.TrialManagers.TrialManager import TrialRecordList


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    soundManager = []
    reinforcementManager = []
    requestPort = 'center'
    frameDropCorner = 'off'
    textureCaches = {}
    phases = []

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(**kwargs)
        tm.soundManager = kwargs['soundManager']
        tm.reinforcementManager = kwargs['reinforcementmanager']
        if 'requestPort'in kwargs:
            tm.requestPort = kwargs['requestPort']

    def stationOKForTrialManager(tm, st):
        return False

    def doTrial(tm, ts, p, sub, tR, cR):
        # tm - trialManager
        # ts - trainingStep
        # p - protocol
        # sub - subject
        # tR - trialRecord (current)
        # sR - sessionRecord
        # cR - compiledRecord
        tm._setupPhases()

    def _setupPhases(tm):
        pass


class VisionBehaviorTrialRecord(TrialRecord):
    """
    """
    response = 0
    step = ''
    responseTime = 0
    phaseRecords = []


class VisionBehaviorTrialRecordList(TrialRecordList):
    pass