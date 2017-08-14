from .TrialManager import TrialManager
from verlib import NormalizedVersion as Ver

doNothing = []


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    SoundManager = []
    ReinforcementManager = []
    RequestPort = 'center'  # 'center' or 'all' or 'none'
    FrameDropCorner = 'off'
    TextureCaches = []
    Phases = []

    ver = Ver('0.0.1')

    allowRepeats = True

    def __init__(tm, **kwargs):
        super(StandardVisionBehaviorTrialManager, tm).__init__(**kwargs)
        tm.SoundManager = kwargs['soundManager']
        tm.ReinforcementManager = kwargs['reinforcementmanager']
        if 'requestPort'in kwargs:
            tm.RequestPort = kwargs['requestPort']
        if 'frameDropCorner' in kwargs:
            tm.FrameDropCorner = kwargs['frameDropCorner']

    def doTrial(tm, **kwargs):
        # tm - trialManager
        # st - station
        # p - protocol
        # sub - subject
        # tR - trialRecord (current)
        # cR - compiledRecord
        # tR = kwargs['trialRecords']  # need to send this to _setupPhases
        tm._setupPhases(kwargs)  # should call calcStim
        tm._validatePhases()
        tm._stationOKForTrialManager(kwargs['station'])

        # important data common to all trials
        tR = kwargs['trialRecords']
        tR.reinforcementManagerName = tm.ReinforcementManager.name
        tR.reinforcementManagerClass = \
            tm.ReinforcementManager.__class__.__name__

    def decache(tm):
        tm.TextureCaches = []
        return tm

    def _setupPhases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on a',
            ' concrete example')

    def compileRecords(tm):
        pass


