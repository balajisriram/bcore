class PhaseSpecs(object):
    """
        PHASESPEC acts as a kind of state machine. You start at the first phase
        which specifies rules for moving through phases and keep going.
        stimType:
            allowed:'static', - explicitly call for flip
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
            to deliver at the beginning of the phase. A reward that extends
            beyond the end of the phase is cut off.
        phaseName: a text label for the given phase (stored in phaseRecords)
        isStim: status of station's stim pin for phase(True/ False)
        indexPulses: a boolean vector same length as stimulus
            indicating what to output on the station's indexPin during each
            frame (defaults to all False)
    """
    stimType = 'loop'
    stimulus = {}
    startFrame = 0
    transitions = {}
    framesUntilTransition = float('inf')
    autoTrigger = {}
    scaleFactor = [1, 1]
    isFinalPhase = False
    hz = 60
    phaseType = ''
    phaseName = ''
    isStim = False
    indexPulses = False
    soundPlayed = {}

    def __init__(spec, **kwargs):
        spec.stimulus = kwargs['stimulus']
        spec.stimType = kwargs['stimType']
        spec.startFrame = kwargs['startFrame']
        spec.transitions = kwargs['transitions']
        spec.framesUntilTransition = kwargs['framesUntilTransition']
        spec.autoTrigger = kwargs['autoTrigger']
        spec.scaleFactor = kwargs['scaleFactor']
        spec.isFinalPhase = kwargs['isFinalPhase']
        spec.hz = kwargs['hz']
        spec.phaseType = kwargs['phaseType']
        spec.phaseName = kwargs['phaseName']
        spec.isStim = kwargs['isStim']
        spec.indexPulses = kwargs['indexPulses']
        spec.soundPlayed = kwargs['soundPlayed']