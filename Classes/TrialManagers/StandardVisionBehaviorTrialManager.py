from BCore.Classes.TrialManagers.TrialManager import TrialManager


class PhaseSpecs(object):
    """
        PHASESPEC acts as a kind of state machine. You start at the first phase
        stimType:
            allowed: 'static', - explicitly call for flip
                    'cache', - relevant texs are stored in stimManager cache
                    'loop', - given stims are looped
                    {'timedFrames', numFrames}, - present 'numFrames' frames
                    'expert' - use stimManager.drawExpertFrame()
            default is 'loop'
        stimulus: a dictionary containing
            scaleFactor, hz and frames for ('static', 'cache','loop')
                OR
            struct (for 'expert' phase)
        transitions: a dictionary
            {'port1':   target1,
             'port2',   target2,
             'port3',   target3,
             'timeout', target4}  timeout after framesUntilTransition
        framesUntilTransition: used when 'timeout' is specified. Forced to
            float('inf') if no timeout is specified in transitions
        autoTrigger: a dictionary
            {'port1':   p1,
             'port2',   p2,
             'port3',   p3}
        isFinalPhase: a flag if this is the final phase of the trial
        phaseType: one of {'reinforced', None} --
            reinforced will ask the reinforcement manager how much water/airpuff
            to deliver at the beginning of the phase. Areward that extends
            beyond the end of the phase is cut off.
        phaseName: a text label for the given phase (stored in phaseRecords)
        isStim: status of station's stim pin for phase(True/ False)
        indexPulses: a boolean vector same length as stimulus
            indicating what to output on the station's indexPin during each
            frame (defaults to all False)
    """
    stimType = 'loop'
    stimulus = {}
    transitions = {}
    framesUntilTransition = float('inf')
    autoTrigger = {}
    isFinalPhase = False
    phaseType = ''
    phaseName = ''
    isStim = False
    indexPulses = False


class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    name = ''
    textDisplay = 'full'
    stimManager = []
    soundManager = []
    reinforcementManager = []
    requestPort = 'center'  # 'center' or 'all'
    frameDropCorner = 'off'
    textureCaches = {}
    stimSpec = []

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
        tm._validatePhases()

    def _setupPhases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on\
        a concrete example')

    def compileRecords(tm):
        pass