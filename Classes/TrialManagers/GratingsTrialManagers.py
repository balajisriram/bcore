from verlib import NormalizedVersion as Ver
from .PhaseSpec import PhaseSpec
from ..ReinforcementManager import ConstantReinforcement
from ..Station import StandardKeyboardStation
import psychopy
import random
import numpy
import psychopy.visual,psychopy.core
import pdb
from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED,
                                NOT_STARTED, FOREVER)

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

"""
    TODOs:
    1. All Ver should be inside the init - Keeping it outside make them irrelevant
    2. Figure out a way to send subject into _setup_phases. Need it for reward and timeout values
"""
class Gratings(object):
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
    _Cached_Stimuli = None
    
    def __init__(self,
                 name,
                 deg_per_cycs=[10], #degrees
                 orientations=[45], #degrees
                 drift_frequencies=[0], #hz
                 phases=[0],
                 contrasts=[1],
                 durations=[1], #seconds
                 radii=[400], #degrees
                 iti=1, #seconds
                 itl=0.2, #inter trial luminance
                 **kwargs):
        super(Gratings, self).__init__(**kwargs)
        
        self.name = name
        self.deg_per_cycs = deg_per_cycs
        self.orientations = orientations
        self.drift_frequencies = drift_frequencies
        self.phases = phases
        self.contrasts = contrasts
        self.durations = durations
        self.radii = radii

        self.iti = iti # inter trial interval (s)
        
        if numpy.isscalar(itl):
            self.itl = itl*numpy.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = numpy.asarray(itl) #itl as color

    def calc_stim(self, trial_record, station, **kwargs):

        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        target_ports = None
        distractor_ports = station.get_ports()
        
        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs)
        stimulus['orientation'] = random.choice(self.orientations)
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies)
        stimulus['phase'] = random.choice(self.phases)
        stimulus['contrast'] = random.choice(self.contrasts)
        stimulus['duration'] = random.choice(self.durations)
        stimulus['radius'] = random.choice(self.radii)
        stimulus['H'] = H
        stimulus['W'] = W
        stimulus['Hz'] = Hz
        
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
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        self._Phases = []
        # Just display stim
        do_nothing = ()
        print('iti::',self.iti)
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',mask=None,autoLog=False),
            stimulus_update_fn=Gratings.update_stimulus,
            stimulus_details=stimulus_details,
            transitions={do_nothing: 1},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='stim',
            hz=hz,
            sounds_played=(station._sounds['trial_start_sound'], 0.050)))
        self._Phases.append(PhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=Gratings.do_nothing_to_stim,
            transitions={do_nothing: 2},
            frames_until_transition=round(self.iti*hz),
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='inter-trial',
            hz=hz,
            sounds_played=(station._sounds['trial_end_sound'], 0.050)))
        
    def _simulate(self):
        station = StandardKeyboardStation()
        station.initialize()
        trial_record = {}
        Quit = False
        while not Quit:
            trial_record,Quit = self.do_trial(trial_record=trial_record,station=station,subject=None,compiled_record=None)
        station.close_window()

    def decache(self):
        self._Phases = dict()
        
    @staticmethod
    def update_stimulus(stimulus,details):
        if details['drift_frequency'] !=0:
            stimulus.phase += float(details['drift_frequency'])/float(details['Hz'])
            
    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass
    
    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl
                
        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record)
        station._key_pressed = []
        
        for phase in self._Phases:
            frames_until_transition = phase.frames_until_transition
            phase_done = False
            sound = phase.sounds_played
            stim = phase.stimulus
            stim_details = phase.stimulus_details
            if phase.sounds_played:
                sound = phase.sounds_played[0]
                sound_duration = phase.sounds_played[1]
                sound.seek(0.)
                sound_started = False
                sound_done = False
                sound_timer = psychopy.core.CountdownTimer(sound_duration)
            else:
                sound = None
            
            while not phase_done:    
                # deal with sounds
                if sound:
                    if not sound_started:
                        sound.play()
                        sound_timer.reset()
                        sound_started = True
                        
                    if sound_timer.getTime() <0 and not sound_done:
                        sound.stop()
                        sound_done = True
                
                # deal with stim
                if stim:
                    stim.draw()
                    phase.stimulus_update_fn(stim,stim_details)
                station._window.flip()
            
                # update the frames
                frames_until_transition = frames_until_transition-1
                if frames_until_transition==0: phase_done = True
                quit = quit or station.check_manual_quit()
            
        return trial_record,quit

class Gratings_GaussianEdge(Gratings):
    """
        GRATINGS_GAUUIANEDGE defines a standard gratings trial manager
        with a gaussian edge for a view port

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """

    ver = Ver('0.0.1')

    def __init__(self, name, **kwargs):
        super(Gratings_GaussianEdge, self).__init__(name, **kwargs)

    def _setup_phases(self, trial_record, station, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        self._Phases = []
        # Just display stim
        do_nothing = ()
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',mask='gauss',autoLog=False),
            stimulus_update_fn=Gratings.update_stimulus,
            stimulus_details=stimulus_details,
            transitions={do_nothing: 1},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='stim',
            hz=hz,
            sounds_played=(station._sounds['trial_start_sound'], 0.050)))
        self._Phases.append(PhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=Gratings.do_nothing_to_stim,
            transitions={do_nothing: 2},
            frames_until_transition=round(self.iti*hz),
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='inter-trial',
            hz=hz,
            sounds_played=(station._sounds['trial_end_sound'], 0.050)))
    

class Gratings_HardEdge(Gratings):
    """
        GRATINGS_HARDEDGE defines a standard gratings trial manager
        with hard edges for a view port

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """
    ver = Ver('0.0.1')

    def __init__(self, name, **kwargs):
        super(Gratings_HardEdge, self).__init__(name, **kwargs)
    
    def _setup_phases(self, trial_record, station, **kwargs):
        """
        Gratings:_setupPhases is a simple trialManager. It is for autopilot
        It selects from PixPerCycs, Orientations, DriftFrequencies, Phases
        Contrasts, Durations and shows them one at a time. There is only one
        phase. There is no "correct" and no responses are required/recorded
        """
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        self._Phases = []
        # Just display stim
        do_nothing = ()
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',mask='circle',autoLog=False),
            stimulus_update_fn=Gratings.update_stimulus,
            stimulus_details=stimulus_details,
            transitions={do_nothing: 1},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='stim',
            hz=hz,
            sounds_played=(station._sounds['trial_start_sound'], 0.050)))
        self._Phases.append(PhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=Gratings.do_nothing_to_stim,
            transitions={do_nothing: 2},
            frames_until_transition=round(self.iti*hz),
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='inter-trial',
            hz=hz,
            sounds_played=(station._sounds['trial_end_sound'], 0.050)))
    
 
class AFCGratings(object):
    """
        AFCGRATINGS defines a standard gratings trial manager
            deg_per_cycs
            orientations
            drift_frequencies
            phases
            contrasts
            durations
            radii # in units of "Scale"
            positions
    """
    ver = Ver('0.0.1')
    _Phases = []

    def __init__(self,
                 deg_per_cycs = {'L':[10],'R':[10]},
                 orientations = {'L':[-numpy.pi / 4], 'R':[numpy.pi / 4]},
                 drift_frequencies = {'L':[0],'R':[0]},
                 phases = {'L':numpy.linspace(start=-numpy.pi,stop=numpy.pi,num=8,endpoint=True),'R':numpy.linspace(start=-numpy.pi,stop=numpy.pi,num=8, endpoint=True)},
                 contrasts = {'L':[1],'R':[1]},
                 durations = {'L':[float('Inf')],'R':[float('Inf')]},
                 locations = {'L':[(0.5,0.5)],'R':[(0.5,0.5)]},
                 radii = {'L':[40],'R':[40]},
                 iti = 1,
                 itl = 0.5,
                 do_combos = True,
                 reinforcement_manager = ConstantReinforcement(),
                 **kwargs):
        self.do_combos = do_combos
        self.deg_per_cycs = deg_per_cycs
        self.orientations = orientations
        self.drift_frequencies = drift_frequencies
        self.phases = phases
        self.contrasts = contrasts
        self.durations = durations
        self.locations = locations
        self.radii = radii

        self.iti = iti # inter trial interval (s)
        
        if numpy.isscalar(itl):
            self.itl = itl*numpy.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = numpy.asarray(itl) #itl as color
        
        n_afc = len(deg_per_cycs)
        assert len(self.orientations)==n_afc,'orientations not same length as %r' % n_afc
        assert len(self.driftfrequencies)==n_afc,'driftfrequencies not same length as %r' % n_afc
        assert len(self.phases)==n_afc,'phases not same length as %r' % n_afc
        assert len(self.contrasts)==n_afc,'contrasts not same length as %r' % n_afc
        assert len(self.durations)==n_afc,'durations not same length as %r' % n_afc
        assert len(self.locations)==n_afc,'locations not same length as %r' % n_afc
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
            assert len(self.locations['L'])==num_options_L,'L locations not same length as deg_per_cycs'
            assert len(self.radii['L'])==num_options_L,'L radii not same length as deg_per_cycs'
            
            num_options_R = len(self.deg_per_cycs['R'])
            assert len(self.orientations['R'])==num_options_R,'R orientations not same length as deg_per_cycs'
            assert len(self.driftfrequencies['R'])==num_options_R,'R driftfrequencies not same length as deg_per_cycs'
            assert len(self.phases['R'])==num_options_R,'R phases not same length as deg_per_cycs'
            assert len(self.contrasts['R'])==num_options_R,'R contrasts not same length as deg_per_cycs'
            assert len(self.durations['R'])==num_options_R,'R durations not same length as deg_per_cycs'
            assert len(self.locations['R'])==num_options_R,'R locations not same length as deg_per_cycs'
            assert len(self.radii['R'])==num_options_R,'R radii not same length as deg_per_cycs'
            
    @property
    def n_afc():
        return len(self.deg_per_cycs)
        
    def calc_stim(self, tR, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(kwargs)
        all_ports = ['L','C','R']
        request_ports = ['C']
        response_ports = numpy.setdiff1d(all_ports,request_ports)
        target_ports = numpy.random.choice(response_ports)
        distractor_ports = numpy.setdiff1d(response_ports,target_ports)
        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs[target_ports])
        stimulus['orientation'] = random.choice(self.orientations[target_ports])
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies[target_ports])
        stimulus['phase'] = random.choice(self.phases[target_ports])
        stimulus['contrast'] = random.choice(self.contrasts[target_ports])
        stimulus['duration'] = random.choice(self.durations[target_ports])
        stimulus['location'] = random.choice(self.locations[target_ports])
        stimulus['radius'] = random.choice(self.radii[target_ports])
        stimulus['H'] = H
        stimulus['W'] = W
        stimulus['Hz'] = Hz
        
        target_ports = [target_ports]
        
        trial_record['chosen_stim'] = stimulus

        frames_total = round(Hz*stimulus['duration'])
        
        port_details = {}
        port_details['request_port'] = request_port
        port_details['target_ports'] = target_ports
        port_details['distractor_ports'] = distractor_ports

        return stimulus, resolution, frames_total, port_details
        
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
        (stimulus_details, resolution, frames_total, port_details) = gratings.calc_stim(kwargs)
        if stimulus_details['duration']==inf:
            do_post_discrim_stim = False
            quit_check_every_frame = True
        else:
            do_post_discrim_stim = True
            quit_check_every_frame = False
            
        self._Phases = []
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=Gratings.update_stimulus,
            stimulus_details=stimulus_details,
            transitions={port_details['request_port']: 2},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='pre-request',
            phase_name='pre-request',
            hz=hz,
            sounds_played=(station._sounds['trial_start_sound'], 0.050)))
        self._Phases.append(PhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',mask=None,autoLog=False),
            stimulus_update_fn=Gratings.update_stimulus,
            stimulus_details=stimulus_details,
            transitions={do_nothing: 1},
            frames_until_transition=frames_total,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='stim',
            hz=hz,
            sounds_played=(station._sounds['trial_start_sound'], 0.050)))
        self._Phases.append(PhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=Gratings.do_nothing_to_stim,
            transitions={do_nothing: 2},
            frames_until_transition=round(self.iti*hz),
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='inter-trial',
            hz=hz,
            sounds_played=(station._sounds['trial_end_sound'], 0.050)))
           
if __name__=='__main__':
    g = Gratings_GaussianEdge('SampleGratingsGaussianEdge',
                 deg_per_cycs=[0.01,0.1,1], #cpd?
                 orientations=[-45,-22.5,0,22.5,45], #degrees
                 drift_frequencies=[0,1], #hz
                 phases=[0],
                 contrasts=[1,0.15],
                 durations=[1], #seconds
                 radii=[200], #degrees
                 iti=1, #seconds
                 itl=0.5, #inter trial luminance
                 )
    
    g._simulate()
