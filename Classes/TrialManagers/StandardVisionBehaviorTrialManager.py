from BCore.Classes.TrialManagers.TrialManager import TrialManager


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    soundManager = []
    reinforcementManager = []
    requestPort = 'center'  # 'center' or 'all'
    frameDropCorner = 'off'
    textureCaches = []
    phases = []

    allowRepeats = True

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(**kwargs)
        tm.soundManager = kwargs['soundManager']
        tm.reinforcementManager = kwargs['reinforcementmanager']
        if 'requestPort'in kwargs:
            tm.requestPort = kwargs['requestPort']
        if 'frameDropCorner' in kwargs:
            tm.frameDropCorner = kwargs['frameDropCorner']

    def doTrial(tm, **kwargs):
        # tm - trialManager
        # st - station
        # p - protocol
        # sub - subject
        # tR - trialRecord (current)
        # cR - compiledRecord
        tm._setupPhases()
        tm._validatePhases()

    def _setupPhases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on\
        a concrete example')

    def compileRecords(tm):
        pass


class Gratings(StandardVisionBehaviorTrialManager):

    def __init__(grating, **kwargs):
        super(StandardVisionBehaviorTrialManager, grating).__init__(**kwargs)

