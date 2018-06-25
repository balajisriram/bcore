from .StandardVisionBehaviorTrialManager import StandardVisionBehaviorTrialManager
from verlib import NormalizedVersion as Ver
from .PhaseSpec import PhaseSpec
from ..ReinforcementManager import ConstantReinforcement
import psychopy
import random
import numpy

PI = 3.14159

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class Gratings(StandardVisionBehaviorTrialManager):
    """
        GRATINGS defines a standard gratings trial manager
            deg_per_cycs
            orientations
            drift_frequencies
            phases
            contrasts
            durations
            radii

    """
    ver = Ver('0.0.1')
    _Phases = None
    _Cached_Textures = None
    
    def __init__(self,
                 deg_per_cycs=10, #degrees
                 orientations=45, #degrees
                 drift_frequencies=0, #hz
                 phases=0,
                 contrasts=1,
                 durations=1, #seconds
                 radii=40, #degrees
                 iti=1, #seconds
                 **kwargs):
        super(Gratings, self).__init__(**kwargs)

        self.deg_per_cycs = deg_per_cycs
        self.orientations = orientations
        self.drift_frequencies = drift_frequencies
        self.phases = phases
        self.contrasts = contrasts
        self.durations = durations
        self.radii = radii

        self.iti = iti # inter trial interval

    def calc_stim(self, trial_record, station, **kwargs):

        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        trial_record['resolution'] = resolution

        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs)
        stimulus['orientation'] = random.choice(self.orientations)
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies)
        stimulus['phase'] = random.choice(self.phases)
        stimulus['contrast'] = random.choice(self.contrasts)
        stimulus['duration'] = random.choice(self.durations)
        stimulus['radius'] = random.choice(self.radii)
        trial_record['chosen_stim'] = stimulus

        frames_total = round(Hz*stimulus['duration'])
        
        port_details = {}
        port_details['target_ports'] = None
        port_details['distractor_ports'] = station.get_ports()

        return stimulus, resolution, frames_total, port_details

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setup_phases(self, trial_record, station, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station, kwargs)
        self._Phases = {}
        # Just display stim
        do_nothing = []
        self._Phases[0] = PhaseSpec(
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
        self._Phases[1] = PhaseSpec(
            stimulus=0.5,
            stim_type=('timedFrames',10),
            start_frame=0,
            transitions={do_nothing: 2},
            frames_until_transition=10,
            auto_trigger=False,
            scaleFactor=scaleFactor,
            phase_type='inter-trial',
            phase_name='inter-trial',
            is_stim=False,
            index_pulses =False,
            sound_played=('trialEndSound', 50))

    def _simulate(self, **kwargs):
        pass

    def decache(self):
        self._Phases = dict()
        
    def do_trial(self, station, subject, trial_record, compiled_record):
        ## returns quit and trial_record
        
        ## _setup_phases
        self._setup_phases(trial_record=trial_record, statoin=station,compiled_record=compiled_record)
        self._cache_textures()
        self._cache_sounds()
        
        quit = False
        
        current_phase_num = 0
        manual_quit = False
        manual_reward = False
        
        
                


class AFCGratings(Gratings):
    """
        AFCGRATINGS defines a standard gratings trial manager
            deg_per_cycs
            Orientations
            DriftFrequencies
            Phases
            Contrasts
            Durations
            Radii # in units of "Scale"

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """
    ver = Ver('0.0.1')

    def __init__(self,deg_per_cycs = {'L':[10],'R':[10]},\
    orientations = {'L':[-PI / 4], 'R':[PI / 4]},\
    driftfrequencies = {'L':[0],'R':[0]},\
    phases = {'L':numpy.linspace(start=-PI, stop=PI, num=8, endpoint=True),'R':numpy.linspace(start=-PI, stop=PI, num=8, endpoint=True)},\
    contrasts = {'L':[1],'R':[1]},\
    durations = {'L':[float('Inf')],'R':[float('Inf')]},\
    radii = {'L':[40],'R':[40]},\
    iti = 1,\
    do_combos = True,\
    reinforcement_manager = ConstantReinforcement(),\
    **kwargs):
        super(AFCGratings, self).__init__(deg_per_cycs=deg_per_cycs, #degrees
                                          orientations = orientations, #degrees
                                          driftfrequencies = driftfrequencies, #hz
                                          phases = phases,
                                          contrasts = contrasts,
                                          durations = durations, #seconds
                                          radii = radii, #degrees
                                          iti = iti, #seconds
                                          **kwargs)
        self.do_combos = do_combos
        
        n_afc = len(deg_per_cycs)
        assert len(self.orientations)==n_afc,'orientations not same length as %r' % n_afc
        assert len(self.driftfrequencies)==n_afc,'driftfrequencies not same length as %r' % n_afc
        assert len(self.phases)==n_afc,'phases not same length as %r' % n_afc
        assert len(self.contrasts)==n_afc,'contrasts not same length as %r' % n_afc
        assert len(self.durations)==n_afc,'durations not same length as %r' % n_afc
        assert len(self.radii)==n_afc,'radii not same length as %r' % n_afc
        
        if do_combos:
            # if do_combos, don't have to worry about the lengths of each values
            pass
        else:
            num_options_L = len(self.deg_per_cycs['L'])
            assert len(self.orientations['L'])==num_options_L,'L orientations not same length as deg_per_cycs'
            assert len(self.driftfrequencies['L'])==num_options_L,'L driftfrequencies not same length as deg_per_cycs'
            assert len(self.phases['L'])==num_options_L,'L phases not same length as deg_per_cycs'
            assert len(self.contrasts['L'])==num_options_L,'L contrasts not same length as deg_per_cycs'
            assert len(self.durations['L'])==num_options_L,'L durations not same length as deg_per_cycs'
            assert len(self.radii['L'])==num_options_L,'L radii not same length as deg_per_cycs'
            
            num_options_R = len(self.deg_per_cycs['R'])
            assert len(self.orientations['R'])==num_options_R,'R orientations not same length as deg_per_cycs'
            assert len(self.driftfrequencies['R'])==num_options_R,'R driftfrequencies not same length as deg_per_cycs'
            assert len(self.phases['R'])==num_options_R,'R phases not same length as deg_per_cycs'
            assert len(self.contrasts['R'])==num_options_R,'R contrasts not same length as deg_per_cycs'
            assert len(self.durations['R'])==num_options_R,'R durations not same length as deg_per_cycs'
            assert len(self.radii['R'])==num_options_R,'R radii not same length as deg_per_cycs'
            
    @property
    def n_afc():
        return len(self.deg_per_cycs)
        
    def calc_stim(self, tR, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(kwargs)
        tR.chosen_

    def choose_resolution(gratings, **kwargs):
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