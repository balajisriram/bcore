from BCore.Classes.TrialManagers.TrialManager import TrialManager
from BCore.Classes.TrialManagers.PhaseSpec import PhaseSpecs
from math import pi as PI
from verlib import NormalizedVersion as Ver
import numpy

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


class Gratings(StandardVisionBehaviorTrialManager):
    """
        GRATINGS defines a standard gratings trial manager
            PixPerCycs
            Orientations
            DriftFrequencies
            Phases
            Contrasts
            Durations
            Radii # in units of "Scale"

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """

    PixPerCycs = 128
    Orientations = PI / 4
    DriftFrequencies = 0
    Phases = numpy.linspace(start=-PI, stop=PI, num=8, endpoint=True)
    Contrasts = 1
    Durations = float('Inf')

    ver = Ver('0.0.1')

    def __init__(grating, **kwargs):
        super(StandardVisionBehaviorTrialManager, grating).__init__(**kwargs)

        if 'PixPerCycs'in kwargs:
            grating.PixPerCycs = kwargs['PixPerCycs']
        if 'Orientations' in kwargs:
            grating.Orientations = kwargs['Orientations']
        if 'DriftFrequencies'in kwargs:
            grating.DriftFrequencies = kwargs['DriftFrequencies']
        if 'Phases' in kwargs:
            grating.Phases = kwargs['Phases']
        if 'Contrasts'in kwargs:
            grating.Contrasts = kwargs['Contrasts']
        if 'Durations' in kwargs:
            grating.Durations = kwargs['Durations']

    def CalcStim(gratings, **kwargs):
        tR = kwargs['trialRecord'] # for saving trial specific info

        (H, W, Hz) = gratings.ChooseResolution(kwargs)
        tR.Resolution = (H,W,Hz)
        
        
    def ChooseResolution(gratings, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setupPhases(gratings, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus, stimType, resolution, hz, bitDepth, scaleFactor,
            framesTotal) = gratings.calcStim(kwargs)
        # Just display stim

        gratings.Phases[0] = PhaseSpecs(
            stimulus=stimulus,
            stimType=stimType,
            startFrame=0,
            transitions={doNothing: 1},
            framesUntilTransition=framesTotal,
            autoTrigger=False,
            scaleFactor=scaleFactor,
            phaseType='stimulus',
            phaseName='stim',
            isStim=True,
            indexPulses=False,
            soundPlayed=('trialStartSound', 50))


class AFCGratings(Gratings):
    """
        GRATINGS defines a standard gratings trial manager
            PixPerCycs
            Orientations
            DriftFrequencies
            Phases
            Contrasts
            Durations
            Radii # in units of "Scale"

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """

    PixPerCycs = [[128],[128]]
    Orientations = [[-PI / 4], [PI / 4]]
    DriftFrequencies = [[0],[0]]
    Phases = [numpy.linspace(start=-PI, stop=PI, num=8, endpoint=True),numpy.linspace(start=-PI, stop=PI, num=8, endpoint=True)]
    Contrasts = [[1],[1]]
    Durations = [[float('Inf')],[float('Inf')]]

    ver = Ver('0.0.1')

    def __init__(afcgrating, **kwargs):
        super(Gratings, grating).__init__(**kwargs)

        if 'PixPerCycs'in kwargs:
            grating.PixPerCycs = kwargs['PixPerCycs']
        if 'Orientations' in kwargs:
            grating.Orientations = kwargs['Orientations']
        if 'DriftFrequencies'in kwargs:
            grating.DriftFrequencies = kwargs['DriftFrequencies']
        if 'Phases' in kwargs:
            grating.Phases = kwargs['Phases']
        if 'Contrasts'in kwargs:
            grating.Contrasts = kwargs['Contrasts']
        if 'Durations' in kwargs:
            grating.Durations = kwargs['Durations']

    def CalcStim(gratings, **kwargs):
        (H, W, Hz) = gratings.ChooseResolution(kwargs)

    def ChooseResolution(gratings, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setupPhases(gratings, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus, stimType, resolution, hz, bitDepth, scaleFactor,
            framesTotal) = gratings.calcStim(kwargs)
        # Just display stim

        gratings.Phases[0] = PhaseSpecs(
            stimulus=stimulus,
            stimType=stimType,
            startFrame=0,
            transitions={doNothing: 1},
            framesUntilTransition=framesTotal,
            autoTrigger=False,
            scaleFactor=scaleFactor,
            phaseType='stimulus',
            phaseName='stim',
            isStim=True,
            indexPulses=False,
            soundPlayed=('trialStartSound', 50))


class Gratings_GaussianEdge(Gratings):
    """
        GRATINGS_GAUUIANEDGE defines a standard gratings trial manager
        with a gaussian edge for a view port

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """

    Radii = []
    RadiusType = "GaussianEdge"
    Scale = 'ScaleToHeight'

    ver = Ver('0.0.1')

    def __init__(grating, **kwargs):
        super(Gratings, grating).__init__(**kwargs)

        if 'Radii'in kwargs:
            grating.Radii = kwargs['Radii']


class Gratings_HardEdge(Gratings):
    """
        GRATINGS_HARDEDGE defines a standard gratings trial manager
        with hard edges for a view port

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """

    Radii = []
    RadiusType = "HardEdge"
    ver = Ver('0.0.1')

    def __init__(grating, **kwargs):
        super(Gratings, grating).__init__(**kwargs)

        if 'Radii'in kwargs:
            grating.Radii = kwargs['Radii']