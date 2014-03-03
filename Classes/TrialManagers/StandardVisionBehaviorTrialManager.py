from BCore.Classes.TrialManagers.TrialManager import TrialManager
from BCore.Classes.TrialManagers.TrialManager import TrialRecord
from BCore.Classes.TrialManagers.TrialManager import TrialRecordList

class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__()
        pass
        
        
class VisionBehaviorTrialRecord(TrialRecord):
    """
    """
    response
    step
    responseTime


class VisionBehaviorTrialRecords(TrialRecordList):
    pass