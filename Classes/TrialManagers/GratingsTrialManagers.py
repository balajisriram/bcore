from .StandardVisionBehaviorTrialManager import StandardVisionBehaviorTrialManager
from .PhaseSpec import PhaseSpec
import psychopy
import random

PI = 3.14159

__version__ = '0.0.1'
__author__ = 'Balaji Sriram'


class Gratings(StandardVisionBehaviorTrialManager):
    """
        GRATINGS defines a standard gratings trial manager
            deg_per_cycs
            orientations
            driftfrequencies
            phases
            contrasts
            durations
            radii

    """

    def __init__(self,
                 deg_per_cycs=10, #degrees
                 orientations=45, #degrees
                 driftfrequencies=0, #hz
                 phases=0,
                 contrasts=1,
                 durations=1, #seconds
                 radii=40, #degrees
                 iti=1, #seconds
                 **kwargs):
        super(StandardVisionBehaviorTrialManager, self).__init__(**kwargs)

        self.deg_per_cycs = deg_per_cycs
        self.orientations = orientations
        self.driftfrequencies = driftfrequencies
        self.phases = phases
        self.contrasts = contrasts
        self.durations = durations
        self.radii = radii

        self.iti = iti # inter trial interval

    def calc_stim(self, tR, station, **kwargs):

        (H, W, Hz) = self.choose_resolution(**kwargs)
        resolution = (H,W,Hz)
        tR.resolution = resolution

        # select from values
        stimulus = dict()
        stimulus['pix_per_cyc'] = random.choice(self.pix_per_cycs)
        stimulus['orientation'] = random.choice(self.orientations)
        stimulus['driftfrequency'] = random.choice(self.driftfrequencies)
        stimulus['phase'] = random.choice(self.phases)
        stimulus['contrast'] = random.choice(self.contrasts)
        stimulus['duration'] = random.choice(self.durations)
        stimulus['radius'] = random.choice(self.radii)
        tR.stimulus_details = dict()
        tR.stimulus_details['chosen_stim'] = stimulus


        frames_total = round(Hz*stimulus['duration'])

        return stimulus, resolution, frames_total

    def choose_resolution(self, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setup_phases(self, tR, station, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus, resolution,frames_total) = self.calc_stim(tR, station, kwargs)
        # Just display stim
        do_nothing = []
        self.Phases[0] = PhaseSpec(
            stimulus=stimulus,
            stim_type='dynamic',
            start_frame=0,
            transitions={do_nothing: 1},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='stim',
            is_stim=True,
            index_pulses=False,
            sound_played=('trialStartSound', 50))
        self.Phases[1] = PhaseSpec(
            stimulus=0.5,
            stimType=('timedFrames',10),
            start_frame=0,
            transitions={do_nothing: 2},
            framesUntilTransition=10,
            autoTrigger=False,
            scaleFactor=scaleFactor,
            phaseType='inter-trial',
            phaseName='inter-trial',
            isStim=False,
            indexPulses =False,
            soundPlayed=('trialEndSound', 50))

    def _simulate(self, **kwargs):
        pass

    def decache(self):
        self._internal_objects = dict()


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