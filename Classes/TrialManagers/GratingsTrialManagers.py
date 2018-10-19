from verlib import NormalizedVersion as Ver
from BCore.Classes.TrialManagers.PhaseSpec import PhaseSpec,StimPhaseSpec,RewardPhaseSpec,PunishmentPhaseSpec
from BCore.Classes.ReinforcementManager import ConstantReinforcement,NoReinforcement
from BCore.Classes.Station import StandardKeyboardStation
import psychopy
import random
import numpy as np
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
##########################################################################################
##########################################################################################
######################### GRATINGS TRIAL MANAGERS - SHOWS ################################
############################# ONE GRATING AT A TIME ######################################
##########################################################################################
##########################################################################################

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
    _Phases = None
    _Cached_Stimuli = None

    def __init__(self,
                 name,
                 deg_per_cycs=[10], #degrees
                 orientations=[45], #degrees
                 drift_frequencies=[0], #hz
                 phases=np.linspace(start=-np.pi,stop=np.pi,num=8,endpoint=True),
                 contrasts=[1],
                 durations=[1], #seconds
                 radii=[400], #degrees
                 iti=1, #seconds
                 itl=0.2, #inter trial luminance
                 reinforcement_manager=NoReinforcement(),
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.deg_per_cycs = deg_per_cycs
        self.orientations = orientations
        self.drift_frequencies = drift_frequencies
        self.phases = phases
        self.contrasts = contrasts
        self.durations = durations
        self.radii = radii

        self.iti = iti # inter trial interval (s)

        if np.isscalar(itl):
            self.itl = itl*np.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = np.asarray(itl) #itl as color

    def __repr__(self):
        return "Gratings object with or:%s, tf:%s, ctr:%s and durs:%s)" % (self.orientations, self.drift_frequencies, self.contrasts, self.durations)

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
        self._Phases.append(StimPhaseSpec(
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
            sounds_played=(station._sounds['trial_start_sound'], 0.050),
            is_last_phase=False))
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
            sounds_played=(station._sounds['trial_end_sound'], 0.050),
            is_last_phase=True))

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

        # check if okay to run the trial manager with the station
        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record)
        station._key_pressed = []
        trial_record['enter_trial_loop'] = station._clocks['trial_clock'].getTime()
        trial_record['correct'] = None

        trial_record['reinforcement_manager_name'] = self.reinforcement_manager.name
        trial_record['reinforcement_manager_class'] = self.reinforcement_manager.__class__.__name__
        trial_record['reinforcement_manager_version_number'] = self.reinforcement_manager.ver.__str__()

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
            trial_record = phase.on_enter(station=station,trial_record=trial_record)
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
            trial_record = phase.on_exit(station=station,trial_record=trial_record)

        return trial_record,quit

    @staticmethod
    def trial_compiler(compiled_record,trial_record):
        print('at Gratings trial_compiler')

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionBehaviorStation','StandardVisionHeadfixStation','StandardKeyboardStation']:
            return True
        else:
            return False

class Gratings_GaussianEdge(Gratings):
    """
        GRATINGS_GAUUIANEDGE defines a standard gratings trial manager
        with a gaussian edge for a view port

            RadiusType = "HardEdge"
            Scale = "ScaleToHeight"
    """


    def __init__(self, name, **kwargs):
        self.ver = Ver('0.0.1')
        super(Gratings_GaussianEdge, self).__init__(name, **kwargs)

    def __repr__(self):
        return "Gratings_GaussianEdge object with or:%s, tf:%s, ctr:%s and durs:%s)" % (self.orientations, self.drift_frequencies, self.contrasts, self.durations)

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
        self._Phases.append(StimPhaseSpec(
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
    """

    def __init__(self, name, **kwargs):
        self.ver = Ver('0.0.1')
        super(Gratings_HardEdge, self).__init__(name, **kwargs)

    def __repr__(self):
        return "Gratings_HardEdge object with or:%s, tf:%s, ctr:%s and durs:%s)" % (self.orientations, self.drift_frequencies, self.contrasts, self.durations)

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
        self._Phases.append(StimPhaseSpec(
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

##########################################################################################
##########################################################################################
####################### AFC GRATINGS TRIAL MANAGERS - SHOWS ##############################
############################# ONE GRATING AT A TIME ######################################
##########################################################################################
##########################################################################################

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
    _Phases = []

    def __init__(self,
                 name = 'DemoAFCGratingsTrialManager',
                 deg_per_cycs = {'L':[10],'R':[10]},
                 orientations = {'L':[-np.pi / 4], 'R':[np.pi / 4]},
                 drift_frequencies = {'L':[0],'R':[0]},
                 phases = {'L':np.linspace(start=-np.pi,stop=np.pi,num=8,endpoint=True),'R':np.linspace(start=-np.pi,stop=np.pi,num=8, endpoint=True)},
                 contrasts = {'L':[1],'R':[1]},
                 durations = {'L':[float('Inf')],'R':[float('Inf')]},
                 locations = {'L':[(0.5,0.5)],'R':[(0.5,0.5)]},
                 radii = {'L':[40],'R':[40]},
                 iti = 1,
                 itl = 0.5,
                 do_combos = True,
                 reinforcement_manager = NoReinforcement(),
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.name = name
        self.reinforcement_manager = reinforcement_manager

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

        if np.isscalar(itl):
            self.itl = itl*np.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = np.asarray(itl) #itl as color

        n_afc = len(deg_per_cycs)
        assert len(self.orientations)==n_afc,'orientations not same length as %r' % n_afc
        assert len(self.drift_frequencies)==n_afc,'drift_frequencies not same length as %r' % n_afc
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
            assert len(self.drift_frequencies['L'])==num_options_L,'L drift_frequencies not same length as deg_per_cycs'
            assert len(self.phases['L'])==num_options_L,'L phases not same length as deg_per_cycs'
            assert len(self.contrasts['L'])==num_options_L,'L contrasts not same length as deg_per_cycs'
            assert len(self.durations['L'])==num_options_L,'L durations not same length as deg_per_cycs'
            assert len(self.locations['L'])==num_options_L,'L locations not same length as deg_per_cycs'
            assert len(self.radii['L'])==num_options_L,'L radii not same length as deg_per_cycs'

            num_options_R = len(self.deg_per_cycs['R'])
            assert len(self.orientations['R'])==num_options_R,'R orientations not same length as deg_per_cycs'
            assert len(self.drift_frequencies['R'])==num_options_R,'R drift_frequencies not same length as deg_per_cycs'
            assert len(self.phases['R'])==num_options_R,'R phases not same length as deg_per_cycs'
            assert len(self.contrasts['R'])==num_options_R,'R contrasts not same length as deg_per_cycs'
            assert len(self.durations['R'])==num_options_R,'R durations not same length as deg_per_cycs'
            assert len(self.locations['R'])==num_options_R,'R locations not same length as deg_per_cycs'
            assert len(self.radii['R'])==num_options_R,'R radii not same length as deg_per_cycs'

    def __repr__(self):
        return "AFCGratings object nafc:%s)" % self.n_afc

    @property
    def n_afc():
        return len(self.deg_per_cycs)

    @staticmethod
    def update_stimulus(stimulus,details):
        if details['drift_frequency'] !=0:
            stimulus.phase += float(details['drift_frequency'])/float(details['Hz'])

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass

    def choose_ports(self, trial_record, station, ):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl

        # check if okay to run the trial manager with the station
        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit


        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'L':False, 'C': False, 'R':False}

        # Zero out the trial clock
        trial_clock = station._clocks['trial_clock']
        trial_clock.reset()

        trial_done = False
        error_out = False

        trial_record['errored_out'] = False
        trial_record['manual_quit'] = False


        trial_record['reinforcement_manager_name'] = self.reinforcement_manager.name
        trial_record['reinforcement_manager_class'] = self.reinforcement_manager.__class__.__name__
        trial_record['reinforcement_manager_version_number'] = self.reinforcement_manager.ver.__str__()

        trial_record['phase_data'] = []
        ### loop into trial phases
        while not trial_done and not error_out and not quit:
            # current_phase_num determines the phase
            phase = self._Phases[current_phase_num]

            # collect details about the phase
            frames_until_transition = phase.frames_until_transition
            stim = phase.stimulus
            stim_details = phase.stimulus_details
            transition = phase.transitions
            if not transition:
                is_last_phase = True
            else:
                is_last_phase = False
            auto_trigger = phase.auto_trigger
            if phase.sounds_played:
                sound = phase.sounds_played[0]
                sound_duration = phase.sounds_played[1]
                sound.seek(0.)
                sound_started = False
                sound_done = False
                sound_timer = psychopy.core.CountdownTimer(sound_duration)
            else:
                sound = None

            # save relevant data into phase_data
            phase_data = {}
            phase_data['phase_name'] = phase.phase_name
            phase_data['phase_number'] = phase.phase_number
            phase_data['enter_time'] = trial_clock.getTime()
            phase_data['response'] = []
            phase_data['response_time'] = []

            # loop into phase
            phase_done = False
            trial_record = phase.on_enter(trial_record=trial_record, station=station)
            while not phase_done and not error_out and not quit:
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
                    if phase.phase_name=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
                station._window.flip()

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                elif len(response)==1:
                    response = response[0]
                    try:
                        current_phase_num = transition[response] - 1
                        response_led_to_transition = True
                    except KeyError:
                        response_led_to_transition = False # that phase did not have a transition for that response
                    except TypeError:
                        assert is_last_phase, 'No reason why it should come here otherwise'
                    finally:
                        # logit but only if was_on wasnt already on
                        if not was_on[response]:
                            phase_data['response'].append(response)
                            phase_data['response_time'].append(trial_clock.getTime())
                    was_on[response] = True # flip was on to true after we used it to check for new events
                else:
                    pass

                # update the frames_until_transition and check if the phase is done
                # phase is done when there are no more frames in the phase or is we flipped due to transition
                # however we can stop playing the phase because we manual_quit or because we errored out
                frames_until_transition = frames_until_transition-1
                frames_led_to_transition = False
                if frames_until_transition==0:
                    frames_led_to_transition = True
                    if transition: current_phase_num = transition[None] - 1
                    else: current_phase_num = None # the last phase has no

                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit
            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        return trial_record,quit

    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        all_ports = ('L','C','R')
        request_port = 'C'
        response_ports = tuple(np.setdiff1d(all_ports,request_port))
        target_port = np.random.choice(response_ports)
        distractor_port = tuple(np.setdiff1d(response_ports,target_port))

        distractor_port = distractor_port[0]
        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs[target_port])
        stimulus['orientation'] = random.choice(self.orientations[target_port])
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies[target_port])
        stimulus['phase'] = random.choice(self.phases[target_port])
        stimulus['contrast'] = random.choice(self.contrasts[target_port])
        stimulus['duration'] = random.choice(self.durations[target_port])
        stimulus['location'] = random.choice(self.locations[target_port])
        stimulus['radius'] = random.choice(self.radii[target_port])
        stimulus['H'] = H
        stimulus['W'] = W
        stimulus['Hz'] = Hz

        trial_record['chosen_stim'] = stimulus

        frames_total = round(Hz*stimulus['duration'])

        port_details = {}
        port_details['request_port'] = request_port
        port_details['target_port'] = target_port
        port_details['distractor_port'] = distractor_port

        return stimulus, resolution, frames_total, port_details

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        AFCGratings:_setup_phases
        1. Pre-trial: gray screen. REQUEST_PORT -> 2
        2. Stimulus: Grating stimulus. RESPONSE_PORT==TARGET_PORT -> CORRECT, else PUNISH
        3. Correct: Give reward
        4. Punish: Timeout
        5. ITI: Gray screen of duration iti,
        """
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        if port_details['target_port'] == 'L':
            reward_valve = 'left_valve'
        elif port_details['target_port'] == 'R':
            reward_valve = 'right_valve'
        elif port_details['target_port'] == 'C':
            reward_valve = 'center_valve'

        if stimulus_details['duration']==float('inf'):
            do_post_discrim_stim = False
        else:
            do_post_discrim_stim = True

        self._Phases = []

        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000*60)
        request_reward_size = np.round(request_reward_size/1000*60)
        penalty_size = np.round(ms_penalty/1000*60)
        if do_post_discrim_stim:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                stimulus_update_fn=AFCGratings.update_stimulus,
                stimulus_details=stimulus_details,
                transitions={None: 3, port_details['target_port']: 4, port_details['distractor_port']: 5},
                frames_until_transition=frames_total,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='stim',
                hz=hz,
                sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['target_port']: 4, port_details['distractor_port']: 5},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='post-stimulus',
                phase_name='post-stim',
                hz=hz,
                sounds_played=None))
            self._Phases.append(RewardPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0.,0.,0.,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=6,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                stimulus_update_fn=AFCGratings.update_stimulus,
                stimulus_details=stimulus_details,
                transitions={port_details['target_port']: 3, port_details['distractor_port']: 4},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='stim',
                hz=hz,
                sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(RewardPhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0,0,0,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionBehaviorStation','StandardKeyboardStation']:
            return True
        else:
            return False


##########################################################################################
##########################################################################################
####################### GNG GRATINGS TRIAL MANAGERS - SHOWS ##############################
############################# ONE GRATING AT A TIME ######################################
##########################################################################################
##########################################################################################

class GNGGratings(object):
    """
        GNGGRATINGS defines a standard gratings trial manager for Go-No-Go trials. Requires:
            deg_per_cycs
            orientations
            drift_frequencies
            phases
            contrasts
            durations
            radii # in units of "Scale"
            locations

            do_combos
            reinforcement_manager
    """
    _Phases = []

    def __init__(self,
                 name = 'DemoAFCGratingsTrialManager',
                 deg_per_cycs = {'G':[10],'N':[10]},
                 orientations = {'G':[-np.pi / 4], 'N':[np.pi / 4]},
                 drift_frequencies = {'G':[0],'N':[0]},
                 phases = {'G':np.linspace(start=-np.pi,stop=np.pi,num=8,endpoint=True),'N':np.linspace(start=-np.pi,stop=np.pi,num=8, endpoint=True)},
                 contrasts = {'G':[1],'N':[1]},
                 durations = {'G':[1.],'N':[1.]},
                 locations = {'G':[(0.5,0.5)],'N':[(0.5,0.5)]},
                 radii = {'G':[40],'N':[40]},
                 iti = 1,
                 itl = 0.5,
                 do_combos = True,
                 reinforcement_manager = ConstantReinforcement(),
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.name = name
        self.reinforcement_manager = reinforcement_manager

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

        if np.isscalar(itl):
            self.itl = itl*np.asarray([1,1,1]) # inter trial luminance as gray scale
        else:
            self.itl = np.asarray(itl) #itl as color

        if do_combos:
            # if do_combos, don't have to worry about the lengths of each values
            pass
        else:
            num_options_G = len(self.deg_per_cycs['G'])
            assert len(self.orientations['G'])==num_options_G,'L orientations not same length as deg_per_cycs'
            assert len(self.drift_frequencies['G'])==num_options_G,'L drift_frequencies not same length as deg_per_cycs'
            assert len(self.phases['G'])==num_options_G,'L phases not same length as deg_per_cycs'
            assert len(self.contrasts['G'])==num_options_G,'L contrasts not same length as deg_per_cycs'
            assert len(self.durations['G'])==num_options_G,'L durations not same length as deg_per_cycs'
            assert len(self.locations['G'])==num_options_G,'L locations not same length as deg_per_cycs'
            assert len(self.radii['G'])==num_options_G,'L radii not same length as deg_per_cycs'

            num_options_N = len(self.deg_per_cycs['N'])
            assert len(self.orientations['N'])==num_options_N,'R orientations not same length as deg_per_cycs'
            assert len(self.drift_frequencies['N'])==num_options_N,'R drift_frequencies not same length as deg_per_cycs'
            assert len(self.phases['N'])==num_options_N,'R phases not same length as deg_per_cycs'
            assert len(self.contrasts['N'])==num_options_N,'R contrasts not same length as deg_per_cycs'
            assert len(self.durations['N'])==num_options_N,'R durations not same length as deg_per_cycs'
            assert len(self.locations['N'])==num_options_N,'R locations not same length as deg_per_cycs'
            assert len(self.radii['N'])==num_options_N,'R radii not same length as deg_per_cycs'

        assert np.logical_and(np.all(np.asarray(self.durations['G'])>0), np.all(np.asarray(self.durations['G'])<float('inf'))), 'All durations should be positive and finite'
        assert np.logical_and(np.all(np.asarray(self.durations['N'])>0), np.all(np.asarray(self.durations['N'])<float('inf'))), 'All durations should be positive and finite'

    def __repr__(self):
        return "GNGGratings object"

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

        # check if okay to run the trial manager with the station
        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit


        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'C': False}

        # Zero out the trial clock
        trial_clock = station._clocks['trial_clock']
        trial_clock.reset()

        trial_done = False
        error_out = False

        trial_record['errored_out'] = False
        trial_record['manual_quit'] = False


        trial_record['reinforcement_manager_name'] = self.reinforcement_manager.name
        trial_record['reinforcement_manager_class'] = self.reinforcement_manager.__class__.__name__
        trial_record['reinforcement_manager_version_number'] = self.reinforcement_manager.ver.__str__()

        trial_record['phase_data'] = []
        ### loop into trial phases
        while not trial_done and not error_out and not quit:
            # current_phase_num determines the phase
            phase = self._Phases[current_phase_num]

            # collect details about the phase
            frames_until_transition = phase.frames_until_transition
            stim = phase.stimulus
            stim_details = phase.stimulus_details
            transition = phase.transitions
            if not transition:
                is_last_phase = True
            else:
                is_last_phase = False
            auto_trigger = phase.auto_trigger
            if phase.sounds_played:
                sound = phase.sounds_played[0]
                sound_duration = phase.sounds_played[1]
                sound.seek(0.)
                sound_started = False
                sound_done = False
                sound_timer = psychopy.core.CountdownTimer(sound_duration)
            else:
                sound = None

            # save relevant data into phase_data
            phase_data = {}
            phase_data['phase_name'] = phase.phase_name
            phase_data['phase_number'] = phase.phase_number
            phase_data['enter_time'] = trial_clock.getTime()
            phase_data['response'] = []
            phase_data['response_time'] = []

            # loop into phase
            phase_done = False
            trial_record = phase.on_enter(trial_record=trial_record, station=station)
            while not phase_done and not error_out and not quit:
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
                    if phase.phase_name=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
                station._window.flip()

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                elif len(response)==1:
                    response = response[0]
                    try:
                        current_phase_num = transition[response] - 1
                        response_led_to_transition = True
                    except KeyError:
                        response_led_to_transition = False # that phase did not have a transition for that response
                    except TypeError:
                        assert is_last_phase, 'No reason why it should come here otherwise'
                    finally:
                        # logit but only if was_on wasnt already on
                        if not was_on[response]:
                            phase_data['response'].append(response)
                            phase_data['response_time'].append(trial_clock.getTime())
                    was_on[response] = True # flip was on to true after we used it to check for new events
                else:
                    pass

                # update the frames_until_transition and check if the phase is done
                # phase is done when there are no more frames in the phase or is we flipped due to transition
                # however we can stop playing the phase because we manual_quit or because we errored out
                frames_until_transition = frames_until_transition-1
                frames_led_to_transition = False
                if frames_until_transition==0:
                    frames_led_to_transition = True
                    if transition: current_phase_num = transition[None] - 1
                    else: current_phase_num = None # the last phase has no

                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit
            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        return trial_record,quit

    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        all_ports = ('L','C','R')
        request_port = 'C'
        response_ports = tuple(np.setdiff1d(all_ports,request_port))
        target_port = np.random.choice(response_ports)
        distractor_port = tuple(np.setdiff1d(response_ports,target_port))

        distractor_port = distractor_port[0]
        # select from values
        stimulus = dict()
        stimulus['deg_per_cyc'] = random.choice(self.deg_per_cycs[target_port])
        stimulus['orientation'] = random.choice(self.orientations[target_port])
        stimulus['drift_frequency'] = random.choice(self.drift_frequencies[target_port])
        stimulus['phase'] = random.choice(self.phases[target_port])
        stimulus['contrast'] = random.choice(self.contrasts[target_port])
        stimulus['duration'] = random.choice(self.durations[target_port])
        stimulus['location'] = random.choice(self.locations[target_port])
        stimulus['radius'] = random.choice(self.radii[target_port])
        stimulus['H'] = H
        stimulus['W'] = W
        stimulus['Hz'] = Hz

        trial_record['chosen_stim'] = stimulus

        frames_total = round(Hz*stimulus['duration'])

        port_details = {}
        port_details['request_port'] = request_port
        port_details['target_port'] = target_port
        port_details['distractor_port'] = distractor_port

        return stimulus, resolution, frames_total, port_details

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        AFCGratings:_setup_phases
        1. Pre-trial: gray screen. REQUEST_PORT -> 2
        2. Stimulus: Grating stimulus. RESPONSE_PORT==TARGET_PORT -> CORRECT, else PUNISH
        3. Correct: Give reward
        4. Punish: Timeout
        5. ITI: Gray screen of duration iti,
        """
        (stimulus_details,resolution,frames_total,port_details) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        if port_details['target_port'] == 'L':
            reward_valve = 'left_valve'
        elif port_details['target_port'] == 'R':
            reward_valve = 'right_valve'
        elif port_details['target_port'] == 'C':
            reward_valve = 'center_valve'

        if stimulus_details['duration']==float('inf'):
            do_post_discrim_stim = False
        else:
            do_post_discrim_stim = True

        self._Phases = []

        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000*60)
        request_reward_size = np.round(request_reward_size/1000*60)
        penalty_size = np.round(ms_penalty/1000*60)
        if do_post_discrim_stim:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                stimulus_update_fn=AFCGratings.update_stimulus,
                stimulus_details=stimulus_details,
                transitions={None: 3, port_details['target_port']: 4, port_details['distractor_port']: 5},
                frames_until_transition=frames_total,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='stim',
                hz=hz,
                sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['target_port']: 4, port_details['distractor_port']: 5},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='post-stimulus',
                phase_name='post-stim',
                hz=hz,
                sounds_played=None))
            self._Phases.append(RewardPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0.,0.,0.,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 6},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=6,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={port_details['request_port']: 2},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='pre-request',
                phase_name='pre-request',
                hz=hz,
                sounds_played=(station._sounds['trial_start_sound'], 0.050)))
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.GratingStim(win=station._window,tex='sin',sf=stimulus_details['deg_per_cyc'],size=stimulus_details['radius'],mask='gauss',ori=stimulus_details['orientation'],phase=stimulus_details['phase'],contrast=stimulus_details['contrast'],units='deg',autoLog=False),
                stimulus_update_fn=AFCGratings.update_stimulus,
                stimulus_details=stimulus_details,
                transitions={port_details['target_port']: 3, port_details['distractor_port']: 4},
                frames_until_transition=float('inf'),
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='stim',
                hz=hz,
                sounds_played=(station._sounds['stim_start_sound'], 0.050)))
            self._Phases.append(RewardPhaseSpec(
                phase_number=3,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=reward_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='reward',
                hz=hz,
                sounds_played=(station._sounds['correct_sound'], ms_reward_sound/1000),
                reward_valve=reward_valve))
            self._Phases.append(PunishmentPhaseSpec(
                phase_number=4,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0,0,0,),autoLog=False),
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                stimulus_details=None,
                transitions={None: 5},
                frames_until_transition=penalty_size,
                auto_trigger=False,
                phase_type='reinforcement',
                phase_name='punishment',
                hz=hz,
                sounds_played=(station._sounds['punishment_sound'],ms_penalty_sound/1000)))
            self._Phases.append(PhaseSpec(
                phase_number=5,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
                stimulus_details=None,
                stimulus_update_fn=AFCGratings.do_nothing_to_stim,
                transitions=None,
                frames_until_transition=round(self.iti*hz),
                auto_trigger=False,
                phase_type='inter-trial',
                phase_name='inter-trial',
                hz=hz,
                sounds_played=(station._sounds['trial_end_sound'], 0.050)))

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionBehaviorStation','StandardKeyboardStation']:
            return True
        else:
            return False



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
