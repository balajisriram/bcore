from BCore.Classes.TrialManagers.TrialManager import TrialManager


class StimSpec(object):
    stimulus = 0
    transitions = [[], 0]
    stimType = 'loop'
    startFrame = 1
    framesUntilTransition = float('inf')
    autoTrigger = []
    scaleFactor = 0
    isFinalPhase = False
    hz = 0
    phaseType = ''
    phaseName = ''
    isStim = False
    lockoutDuration = 0

    def __init__(self):
        pass


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    name = ''
    textDisplay = 'full'
    soundManager = []
    reinforcementManager = []
    requestPort = 'center'  # 'center' or 'all'
    frameDropCorner = 'off'
    textureCaches = {}
    phases = []

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(**kwargs)
        tm.soundManager = kwargs['soundManager']
        tm.reinforcementManager = kwargs['reinforcementmanager']
        if 'requestPort'in kwargs:
            tm.requestPort = kwargs['requestPort']

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
        raise NotImplementedError('Cannot run on an abstract class - call on\
        a concrete example')