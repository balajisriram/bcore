from verlib import NormalizedVersion as Ver
from BCore.Classes.TrialManagers.PhaseSpec import PhaseSpec,RewardPhaseSpec,PunishmentPhaseSpec,StimPhaseSpec
from BCore.Classes.ReinforcementManager import ConstantReinforcement,NoReinforcement
from BCore.Classes.Station import StandardKeyboardStation
from BCore.Classes.Subject import DefaultVirtual
import psychopy
import random
import numpy as np
import psychopy.visual,psychopy.core
import pdb
from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED, NOT_STARTED, FOREVER)

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
########################### NO RESPONSE TRIAL MANAGERS ###################################
##########################################################################################

##################################### LICK FOR REWARD ####################################
class LickForReward(object):
    """
        LICKFORREWARD defines a trial manager where rewards are provided for licking
        within a specific time interval. Requires:
            reinforcement_manager: should define reward on a per-trial basis
            trial_start_sound_on: True or False
            delay_distribution: This is the duration to go-signal
                                ('Constant',val)
                                ('Uniform',[lo,hi])
                                ('Gaussian',[mu,sd])
                                ('FlatHazard',[pctile,val,fixed,max])
            punish_delay_response: True or False
            lick_duration: float
            auto_reward: True or False (reward at end of lick duration)
            punish_miss: True or False
    """
    _Phases = None
    _Cached_Stimuli = None
    _simulation = False

    def __init__(self,
                 name,
                 reinforcement_manager=ConstantReinforcement(),
                 trial_start_sound_on = True,
                 delay_distribution = ('Constant',1.),
                 punish_delay_response = False,
                 response_duration = 1.,
                 auto_reward = False,
                 punish_misses = False,
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.trial_start_sound_on = trial_start_sound_on
        self.delay_distribution = delay_distribution
        self.punish_delay_response = punish_delay_response
        self.response_duration = response_duration
        self.auto_reward = auto_reward
        self.punish_misses = punish_misses

        self.itl = (0., 0., 0.,)

        # check if values are ok
        self.verify_params_ok()

    def __repr__(self):
        return "LickForReward trial manager object"

    def verify_params_ok(self):
        assert isinstance(self.trial_start_sound_on,bool),'trial_start_sound_on needs to be boolean'
        assert isinstance(self.punish_delay_response,bool),'punish_delay_response needs to be boolean'
        assert isinstance(self.auto_reward,bool),'auto_reward needs to be boolean'
        assert isinstance(self.punish_misses,bool),'punish_misses needs to be boolean'

        assert self.delay_distribution[0] in ['Constant', 'Uniform', 'Gaussian', 'FlatHazard'], 'what delay distributoin are you using?'

        assert not (self.auto_reward and self.punish_misses), 'No way to auto reward while simultaneously punishing misses'

    def sample_delay(self):
        if self.delay_distribution[0]=='Constant':
            return self.delay_distribution[1]
        elif self.delay_distribution[0]=='Uniform':
            lo = self.delay_distribution[1][0]
            hi = self.delay_distribution[1][1]
            return np.abs(np.random.uniform(low=lo,high=hi))
        elif self.delay_distribution[0]=='Gaussian':
            mu = self.delay_distribution[1][0]
            sd = self.delay_distribution[1][1]
            return np.abs(np.random.normal(loc=mu,scale=sd)) # returning absolute values
        elif self.delay_distribution[0]=='FlatHazard':
            pctile = self.delay_distribution[1][0]
            val = self.delay_distribution[1][1]
            fixed = self.delay_distribution[1][2]
            max = self.delay_distribution[1][3]
            p = -val/np.log(1-pctile)
            delay = fixed+np.random.exponential(p)
            if delay>max: delay=max
            return delay

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        port_details = {}
        port_details['target_ports'] = 'center_port'
        port_details['distractor_ports'] = None

        delay_frame_num = np.round(self.sample_delay()*Hz)
        response_frame_num = np.round(self.response_duration*Hz)

        stimulus = {}
        stimulus['delay_distribution'] = self.delay_distribution
        stimulus['delay_frame_num'] = delay_frame_num
        stimulus['response_frame_num'] = response_frame_num
        stimulus['trial_start_sound_on'] = self.trial_start_sound_on
        stimulus['punish_delay_response'] = self.punish_delay_response
        stimulus['auto_reward'] = self.auto_reward
        stimulus['punish_misses'] = self.punish_misses

        return stimulus,resolution,port_details,delay_frame_num,response_frame_num

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        LickForReward:_setupPhases follows:
            1. Delay Phase with duration sampled from delay_distribution [trial start sound dependent on trial_start_sound_on; punishment dependent on punish_delay_response]
            2. ResponsePhase with a GO sound with duration set by response_duration [reward on response; misses punished based on punish_misses]
            3. Reward phase is standard; Punishment phase based on whether punish_delay_response=True or punish_misses = True
        """
        (stimulus_details,resolution,port_details,delay_frame_num,response_frame_num) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]

        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000*hz)
        ms_penalty = np.round(ms_penalty/1000*hz)

        self._Phases = []
        # Just display stim
        do_nothing = ()

        # sounds
        if self.trial_start_sound_on:
            start_sound = (station._sounds['trial_start_sound'], 0.050)
        else:
            start_sound = None
        go_sound = (station._sounds['go_sound'],0.1)

        # deal with the phases
        # delay phase
        if self.punish_delay_response:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: 1, port_details['target_ports']:3},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay_phase',
                hz=hz,
                sounds_played=start_sound))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: 1},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay_phase',
                hz=hz,
                sounds_played=start_sound))

        # response phase
        if self.punish_misses:
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(1.,1.,1.,),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: 3, port_details['target_ports']:2},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay-stim',
                hz=hz,
                sounds_played=go_sound))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(1.,1.,1.,),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: None, port_details['target_ports']:2},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay-stim',
                hz=hz,
                sounds_played=go_sound))

        # reward phase spec
        self._Phases.append(RewardPhaseSpec(
            phase_number=3,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=LickForReward.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=reward_size,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=(station._sounds['reward_sound'], ms_reward_sound/1000.),
            reward_valve='center_valve'))

        # punishment phase spec
        self._Phases.append(PunishmentPhaseSpec(
            phase_number=4,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(-1.,-1.,-1.,),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=LickForReward.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=ms_penalty,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=(station._sounds['punishment_sound'], ms_penalty_sound/1000.),
            reward_valve='center_valve'))

    def _simulate(self):
        station = StandardKeyboardStation()
        station.initialize()
        station._clocks = {}
        station._clocks['trial_clock'] = psychopy.core.Clock()
        trial_record = {}
        trial_record['trial_number'] = 0
        quit = False
        subject = DefaultVirtual()
        self._simulation = True
        while not quit:
            station._clocks['trial_clock'].reset()
            trial_record,quit = self.do_trial(trial_record=trial_record,station=station,subject=subject,compiled_record=None,quit=quit)
        station.close_window()

    def decache(self):
        self._Phases = dict()

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl
        did_nothing = ()

        # check if okay to run the trial manager with the station
        if not self.station_ok_for_tm(station):
            print('LICKFORREWARD:DO_TRIAL::Station not ok for trial manager')
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record,subject=subject)
        station._key_pressed = []
        trial_record['correct'] = None

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'L':False, 'C': False, 'R':False}

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
            print('LICKFORREWARD:DO_TRIAL::current_phase_num::',current_phase_num)
            print('LICKFORREWARD:DO_TRIAL::frames_until_transition::',frames_until_transition)
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
                    phase.stimulus_update_fn(stim,stim_details)
                phase.on_frame(station=station,trial_record=trial_record)

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
                    if transition: current_phase_num = transition[did_nothing] - 1
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

    @staticmethod
    def trial_compiler(compiled_record,trial_record):
        print('at LickForReward trial_compiler')

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionHeadfixStation','StandardKeyboardStation']:
            return True
        else:
            return False

################################# CLASSICALCONDITIONING ##################################
class ClassicalConditioning(object):
    """
        CLASSICALCONDITIONING defines a trial manager where rewards are provided directly.
        Every trial starts with a random delay, after which auditory go-signal is 
        provided. We measure 
        Requires:
            reinforcement_manager: should define reward on a per-trial basis
            delay_distribution: This is the duration to go-signal
                                ('Constant',val)
                                ('Uniform',[lo,hi])
                                ('Gaussian',[mu,sd])
                                ('FlatHazard',[pctile,val,fixed,max])
            go_signal: can be psychopy.visual object or psychopy.sound object or None
            response_duration: float (seconds)
            
            VERSION HISTORY:
            0.0.1: Basic Functionality circa 12/01/2018
            0.0.2: Reformulated Sound functionality.

            TODO: 
            1. include go_signal. currently only psychopy.visual and psuchopy.sound object
    """
    _Phases = None
    _Cached_Stimuli = None
    def __init__(self,
                 name = 'DefaultCC_ConstantDelay_1s',
                 reinforcement_manager=ConstantReinforcement(),
                 delay_distribution = ('Constant',1.),
                 go_signal = None,
                 response_duration = 2.,**kwargs):
        self.ver = Ver('0.0.2')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.delay_distribution = delay_distribution
        self.go_signal = go_signal
        self.response_duration = response_duration

        self.itl = (0., 0., 0.,)
        self.iti = 1.

        # check if values are ok
        self.verify_params_ok()

    def __repr__(self):
        return "ClassicalConditioning trial manager object"

    def verify_params_ok(self):
        assert self.delay_distribution[0] in ['Constant', 'Uniform', 'Gaussian', 'FlatHazard'], 'what delay distributoin are you using?'

    def sample_delay(self):
        if self.delay_distribution[0]=='Constant':
            return self.delay_distribution[1]
        elif self.delay_distribution[0]=='Uniform':
            lo = self.delay_distribution[1][0]
            hi = self.delay_distribution[1][1]
            return np.abs(np.random.uniform(low=lo,high=hi))
        elif self.delay_distribution[0]=='Gaussian':
            mu = self.delay_distribution[1][0]
            sd = self.delay_distribution[1][1]
            return np.abs(np.random.normal(loc=mu,scale=sd)) # returning absolute values
        elif self.delay_distribution[0]=='FlatHazard':
            pctile = self.delay_distribution[1][0]
            val = self.delay_distribution[1][1]
            fixed = self.delay_distribution[1][2]
            max = self.delay_distribution[1][3]
            p = -val/np.log(1-pctile)
            delay = fixed+np.random.exponential(p)
            if delay>max: delay=max
            return delay

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)
        
    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        port_details = {}
        port_details['target_ports'] = 'center_port'
        port_details['distractor_ports'] = None

        delay_frame_num = np.round(self.sample_delay()*Hz)
        response_frame_num = np.round(self.response_duration*Hz)

        stimulus = {}
        stimulus['delay_distribution'] = self.delay_distribution
        stimulus['delay_frame_num'] = delay_frame_num
        stimulus['response_frame_num'] = response_frame_num

        return stimulus,resolution,port_details,delay_frame_num,response_frame_num

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        ClassicalConditioning:_setupPhases follows:
            1. Delay Phase with duration sampled from delay_distribution
            2. ResponsePhase with a GO sound with duration set by response_duration
            3. Reward phase is standard
        """
        (stimulus_details,resolution,port_details,delay_frame_num,response_frame_num) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000*hz)

        self._Phases = []
        # Just display stim
        do_nothing = ()

        # sounds
        go_sound = station._sounds['go_sound']
        go_sound.secs = 0.1
        go_sound.seek(0.)
        go_sound.status = NOT_STARTED
        reward_sound = station._sounds['reward_sound']
        reward_sound.secs = ms_reward_sound/1000.
        reward_sound.seek(0.)
        reward_sound.status = NOT_STARTED

       
        # deal with the phases
        # delay phase
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=ClassicalConditioning.do_nothing_to_stim,
            stimulus_details=None,
            transitions={do_nothing: 1},
            frames_until_transition=delay_frame_num,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=None))

        # response phase
        self._Phases.append(StimPhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=ClassicalConditioning.do_nothing_to_stim,
            stimulus_details=None,
            transitions={do_nothing: 2},
            frames_until_transition=response_frame_num,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='delay-stim',
            hz=hz,
            sounds_played=[go_sound]))

        # reward phase spec
        self._Phases.append(RewardPhaseSpec(
            phase_number=3,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=ClassicalConditioning.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=reward_size,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=[reward_sound],
            reward_valve='reward_valve'))

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl

        # check if okay to run the trial manager with the station

        """
            TODO: should running port be part of the logic??
        """
        from psychopy import logging
        logging.console.setLevel(logging.ERROR)

        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        do_nothing = ()

        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'response_port':False}

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

        station.set_trial_pin_on()
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
                if phase.sounds_played:
                    for snd in phase.sounds_played:
                        if snd.status==NOT_STARTED: snd.play()
                # deal with stim
                if stim:
                    stim.draw()
                    if phase.phase_name=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
                phase.on_frame(station=station,trial_record=trial_record)

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                    print('ClassicalConditioning:do_trial:errored out')
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
                if frames_until_transition==0 and transition and do_nothing in transition:
                    frames_led_to_transition = True
                    current_phase_num = transition[do_nothing]
                elif frames_until_transition==0 and transition is None:
                    current_phase_num = None
                    phase_done = True
                    trial_done = True
                    print('end of trial')
                else:
                    RuntimeError("transition cannot have frames go to zero without a do_nothing possibility")
                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    print('manual_quitted')
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit
                
                if (phase_done or quit) and phase.sounds_played:
                    for snd in phase.sounds_played: snd.stop()

            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        station.set_trial_pin_off()
        return trial_record,quit

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardKeyboardStation','StandardVisionHeadfixStation']:
            return True
        else:
            return False


class AuditoryGoOnly(object):
    """
        AUDITORYGOONLY defines a trial manager Auditory go signals require response for
        reward. Absence of response leads to error sounds
        Requires:
            reinforcement_manager: should define reward on a per-trial basis
            delay_distribution: This is the duration to go-signal
                                ('Constant',val)
                                ('Uniform',[lo,hi])
                                ('Gaussian',[mu,sd])
                                ('FlatHazard',[pctile,val,fixed,max])
            go_signal: can be psychopy.visual object or psychopy.sound object or None
            response_duration: float (seconds)
            
            VERSION HISTORY:
            0.0.1: Basic Functionality circa 12/13/2018

            TODO: 
            1. include go_signal. currently only psychopy.visual and psuchopy.sound object
    """
    _Phases = None
    _Cached_Stimuli = None
    def __init__(self,
                 name = 'DefaultAuditory_Go_ConstantDelay_2s',
                 reinforcement_manager=ConstantReinforcement(),
                 delay_distribution = ('Constant',2.),
                 go_signal = None,
                 response_duration = 2.,**kwargs):
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.delay_distribution = delay_distribution
        self.go_signal = go_signal
        self.response_duration = response_duration

        self.itl = (0., 0., 0.,)
        self.iti = 1.

        # check if values are ok
        self.verify_params_ok()

    def __repr__(self):
        return "AuditoryGoOnly trial manager object"

    def verify_params_ok(self):
        assert self.delay_distribution[0] in ['Constant', 'Uniform', 'Gaussian', 'FlatHazard'], 'what delay distributoin are you using?'

    def sample_delay(self):
        if self.delay_distribution[0]=='Constant':
            return self.delay_distribution[1]
        elif self.delay_distribution[0]=='Uniform':
            lo = self.delay_distribution[1][0]
            hi = self.delay_distribution[1][1]
            return np.abs(np.random.uniform(low=lo,high=hi))
        elif self.delay_distribution[0]=='Gaussian':
            mu = self.delay_distribution[1][0]
            sd = self.delay_distribution[1][1]
            return np.abs(np.random.normal(loc=mu,scale=sd)) # returning absolute values
        elif self.delay_distribution[0]=='FlatHazard':
            pctile = self.delay_distribution[1][0]
            val = self.delay_distribution[1][1]
            fixed = self.delay_distribution[1][2]
            max = self.delay_distribution[1][3]
            p = -val/np.log(1-pctile)
            delay = fixed+np.random.exponential(p)
            if delay>max: delay=max
            return delay

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)
        
    def calc_stim(self, trial_record, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        port_details = {}
        port_details['target_ports'] = 'response_port'
        port_details['distractor_ports'] = None

        delay_frame_num = np.round(self.sample_delay()*Hz)
        response_frame_num = np.round(self.response_duration*Hz)

        stimulus = {}
        stimulus['delay_distribution'] = self.delay_distribution
        stimulus['delay_frame_num'] = delay_frame_num
        stimulus['response_frame_num'] = response_frame_num
        return stimulus,resolution,port_details,delay_frame_num,response_frame_num

    def _setup_phases(self, trial_record, station, subject, **kwargs):
        """
        AuditoryGo:_setupPhases follows:
            1. Delay Phase with duration sampled from delay_distribution
            2. ResponsePhase with a GO sound with duration set by response_duration.
            3    a. Response during response duration -> reward
                 b. No response during response duration -> error sound
            4. ITL   
        """
        (stimulus_details,resolution,port_details,delay_frame_num,response_frame_num) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]
        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = np.round(reward_size/1000.*hz)
        penalty_size = np.round(ms_penalty/1000.*hz)
        iti_size = np.round(self.iti*hz)

        self._Phases = []
        # Just display stim
        do_nothing = ()

        # sounds
        go_sound = station._sounds['go_sound']
        go_sound.secs = 0.1
        go_sound.seek(0.)
        go_sound.status = NOT_STARTED
        reward_sound = station._sounds['reward_sound']
        reward_sound.secs = ms_reward_sound/1000.
        reward_sound.seek(0.)
        reward_sound.status = NOT_STARTED
        punishment_sound = station._sounds['punishment_sound']
        punishment_sound.seek(0.)
        punishment_sound.status = NOT_STARTED

       
        # deal with the phases
        # delay phase
        self._Phases.append(PhaseSpec(
            phase_number=1,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=AuditoryGoOnly.do_nothing_to_stim,
            stimulus_details=None,
            transitions={do_nothing: 1},
            frames_until_transition=delay_frame_num,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=None))

        # response phase
        self._Phases.append(StimPhaseSpec(
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=AuditoryGoOnly.do_nothing_to_stim,
            stimulus_details=None,
            transitions={port_details['target_ports']: 2, do_nothing: 3},
            frames_until_transition=response_frame_num,
            auto_trigger=False,
            phase_type='stimulus',
            phase_name='delay-stim',
            hz=hz,
            sounds_played=[go_sound]))

        # reward phase spec
        self._Phases.append(RewardPhaseSpec(
            phase_number=3,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=AuditoryGoOnly.do_nothing_to_stim,
            transitions={do_nothing: 4},
            frames_until_transition=reward_size,
            auto_trigger=False,
            phase_type='reinforcement',
            phase_name='reward_phase',
            hz=hz,
            sounds_played=[reward_sound],
            reward_valve='reward_valve'))
            
        # punishment phase spec
        self._Phases.append(PunishmentPhaseSpec(
            phase_number=4,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=AuditoryGoOnly.do_nothing_to_stim,
            transitions={do_nothing: 4},
            frames_until_transition=penalty_size,
            auto_trigger=False,
            phase_type='reinforcement',
            phase_name='punishment_phase',
            hz=hz,
            sounds_played=[punishment_sound]))
            
        # itl
        self._Phases.append(PhaseSpec(
            phase_number=5,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=AuditoryGoOnly.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=iti_size,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='iti_phase',
            hz=hz,
            sounds_played=None))

    @staticmethod
    def do_nothing_to_stim(stimulus,details):
        pass

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl

        # check if okay to run the trial manager with the station

        """
            TODO: should running port be part of the logic??
        """
        from psychopy import logging
        logging.console.setLevel(logging.ERROR)

        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        do_nothing = ()

        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        current_phase_num = 0

        # was on will be used to check for new responses
        was_on = {'response_port':False}

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

        station.set_trial_pin_on()
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
                if phase.sounds_played:
                    for snd in phase.sounds_played:
                        if snd.status==NOT_STARTED: snd.play()
                # deal with stim
                if stim:
                    stim.draw()
                    if phase.phase_name=='stim':
                        psychopy.visual.Rect(station._window,pos=(-300,-300),width=100,height=100,units='pix',fillColor=(1,1,1)).draw()
                    phase.stimulus_update_fn(stim,stim_details)
                phase.on_frame(station=station,trial_record=trial_record)

                # look for responses
                response_led_to_transition = False
                response = station.read_ports()
                if len(response)>1:
                    error_out = True
                    trial_record['errored_out'] = True
                    print('ClassicalConditioning:do_trial:errored out')
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
                if frames_until_transition==0 and transition and do_nothing in transition:
                    frames_led_to_transition = True
                    current_phase_num = transition[do_nothing]
                elif frames_until_transition==0 and transition is None:
                    current_phase_num = None
                    phase_done = True
                    trial_done = True
                    print('end of trial')
                else:
                    RuntimeError("transition cannot have frames go to zero without a do_nothing possibility")
                if frames_led_to_transition or response_led_to_transition:
                    phase_done = True
                manual_quit = station.check_manual_quit()
                if manual_quit:
                    print('manual_quitted')
                    trial_record['manual_quit'] = True
                    trial_record['correct'] = None
                quit = quit or manual_quit
                
                if (phase_done or quit) and phase.sounds_played:
                    for snd in phase.sounds_played: snd.stop()

            trial_record = phase.on_exit(trial_record=trial_record, station=station)
            trial_record['phase_data'].append(phase_data)

            # when do we quit the trial? trial_done only when last phjase
            # but we can exit if manual_quit or errored out
            if is_last_phase: trial_done = True
        station.set_trial_pin_off()
        return trial_record,quit

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardKeyboardStation','StandardVisionHeadfixStation']:
            return True
        else:
            return False


##################################### RUN FOR REWARD #####################################
class RunForReward(object):
    """
        RUNFORREWARD defines a trial manager where rewards are provided for running
        above a specified running speed for a specified duration. Requires:
            reinforcement_manager: should define reward on a per-trial basis
            run_duration_distribution: This is the duration to go-signal
                                ('Constant',val)
                                ('Uniform',[lo,hi])
                                ('Gaussian',[mu,sd])
                                ('FlatHazard',[pctile,val,fixed,max])
            min_run_speed: integer between 0-255 sets the run speed on arduino
    """
    _ino_loaded = False

    def __init__(self,
                 name,
                 reinforcement_manager=ConstantReinforcement(),
                 min_run_speed = 50, # sets_trigger on arduino
                 run_duration_distribution = 2., # seconds
                 **kwargs):
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.run_speed = run_speed
        self.run_duration_distribution = delay_distribution

        self.itl = (0., 0., 0.,)

        if not self.verify_params_ok():
            ValueError('RunForReward::input values are bad')

    def __repr__(self):
        return "RunForReward trial manager"

    def verify_params_ok(self):
        assert self.delay_distribution[0] in ['Constant', 'Uniform', 'Gaussian', 'FlatHazard'], 'what delay distribution are you using?'

    def load_ino(self):
        if not self._ino_loaded:
            ino = self.create_ino()
            val = system(ino)
        if val:self._ino_loaded = True

    def sample_delay(self):
        if self.delay_distribution[0]=='Constant':
            return self.delay_distribution[1]
        elif self.delay_distribution[0]=='Uniform':
            lo = self.delay_distribution[1][0]
            hi = self.delay_distribution[1][1]
            return np.abs(np.random.uniform(low=lo,high=hi))
        elif self.delay_distribution[0]=='Gaussian':
            mu = self.delay_distribution[1][0]
            sd = self.delay_distribution[1][1]
            return np.abs(np.random.normal(loc=mu,scale=sd)) # returning absolute values
        elif self.delay_distribution[0]=='FlatHazard':
            pctile = self.delay_distribution[1][0]
            val = self.delay_distribution[1][1]
            fixed = self.delay_distribution[1][2]
            max = self.delay_distribution[1][3]
            p = -val/np.log(1-pctile)
            delay = fixed+np.random.exponential(p)
            if delay>max: delay=max
            return delay


if __name__=='__main__':
    LFR = LickForReward('DefaultLFR')
    LFR._simulate()
