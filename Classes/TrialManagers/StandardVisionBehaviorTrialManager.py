from BCore.Classes.TrialManagers.TrialManager import TrialManager
from math import pi as PI
import numpy

class StandardVisionBehaviorTrialManager(TrialManager):
    """
        STANDARDVISIONBEHAVIORTRIALMANAGER defines a standard vision
        behavior trial manager.
    """
    SoundManager = []
    ReinforcementManager = []
    RequestPort = 'center'  # 'center' or 'all'
    FrameDropCorner = 'off'
    TextureCaches = []
    Phases = []

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
        tm._setupPhases()
        tm._validatePhases()

    def _setupPhases(tm):
        raise NotImplementedError('Cannot run on an abstract class - call on\
        a concrete example')

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
    Orientations = PI/4
    DriftFrequencies = 0
    Phases = numpy.linspace(start=-PI,stop=PI,num=8,endpoint=True)
    Contrasts = 1
    Durations = float('Inf')


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

    def __init__(grating, **kwargs):
        super(Gratings, grating).__init__(**kwargs)

        if 'Radii'in kwargs:
            grating.Radii = kwargs['Radii']