from verlib import NormalizedVersion as Ver
from .PhaseSpec import PhaseSpec,RewardPhaseSpec,PunishmentPhaseSpec
from ..ReinforcementManager import ConstantReinforcement,NoReinforcement
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
##########################################################################################
##########################################################################################
########################### NO RESPONSE TRIAL MANAGERS ###################################
##########################################################################################
##########################################################################################

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

        self.itl = (0.5, 0.5, 0.5,)

        if not self.verify_params_ok():
            ValueError('LickForReward::input values are bad')

    def verify_params_ok(self):
        assert is_boolean(self.trial_start_sound_on),'trial_start_sound_on needs to be boolean'
        assert is_boolean(self.punish_delay_response),'punish_delay_response needs to be boolean'
        assert is_boolean(self.auto_reward),'auto_reward needs to be boolean'
        assert is_boolean(self.punish_misses),'punish_misses needs to be boolean'

        assert self.delay_distribution[0] in ['Constant', 'Uniform', 'Gaussian', 'FlatHazard'], 'what delay distributoin are you using?'

        assert not (self.auto_reward and self.punish_misses), 'No way to auto reward while simultaneously punishing misses'

    def sample_delay(self):
        if self.delay_distribution[0]=='Constant':
            return self.delay_distribution[1]
        elif self.delay_distribution[0]=='Uniform':
            lo = self.delay_distribution[1][0]
            hi = self.delay_distribution[1][1]
            return numpy.abs(numpy.random.uniform(low=lo,high=hi))
        elif self.delay_distribution[0]=='Gaussian':
            mu = self.delay_distribution[1][0]
            sd = self.delay_distribution[1][1]
            return numpy.abs(numpy.random.normal(loc=mu,scale=sd)) # returning absolute values
        elif self.delay_distribution[0]=='FlatHazard':
            pctile = self.delay_distribution[1][0]
            val = self.delay_distribution[1][1]
            fixed = self.delay_distribution[1][2]
            max = self.delay_distribution[1][3]
            p = -val/numpy.log(1-pctile)
            delay = fixed+numpy.random.exponential(p)
            if delay>max: delay=max
            return delay

    def choose_resolution(self, station, **kwargs):
        H = 1080
        W = 1920
        Hz = 60
        return (H,W,Hz)

    def calc_stim(self, trial_records, station, **kwargs):
        (H, W, Hz) = self.choose_resolution(station=station, **kwargs)
        resolution = (H,W,Hz)
        port_details['target_ports'] = 'center_port'
        port_details['distractor_ports'] = None

        delay_frame_num = numpy.round(self.sample_delay()*Hz)
        response_frame_num = numpy.round(self.response_duration)

        stimulus['delay_distribution'] = delay_distribution
        stimulus['delay_frame_num'] = delay_frame_num
        stimulus['response_frame_num'] = response_frame_num
        stimulus['trial_start_sound_on'] = trial_start_sound_on
        stimulus['punish_delay_response'] = punish_delay_response
        stimulus['auto_reward'] = auto_reward
        stimulus['punish_misses'] = punish_misses

        return stimulus,resolution,port_details,delay_frame_num,response_frame_num

    def _setup_phases(self, trial_record, station, **kwargs):
        """
        LickForReward:_setupPhases follows:
            1. Delay Phase with duration sampled from delay_distribution [trial start sound dependent on trial_start_sound_on; punishment dependent on punish_delay_response]
            2. ResponsePhase with a GO sound with duration set by response_duration [reward on response; misses punished based on punish_misses]
            3. Reward phase is standard; Punishment phase based on whether punish_delay_response=True or punish_misses = True
        """
        (stimulus_details,resolution,port_details,delay_frame_num,response_frame_num) = self.calc_stim(trial_record=trial_record, station=station)
        hz = resolution[2]

        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = self.reinforcement_manager.calculate_reinforcement(subject=subject)
        reward_size = numpy.round(reward_size/1000*hz)
        ms_penalty = numpy.round(ms_penalty/1000*hz)

        self._Phases = []
        # Just display stim
        do_nothing = ()
        if self.trial_start_sound_on:
            start_sound = (station._sounds['trial_start_sound'], 0.050)
        else:
            start_sound = None

        # delay phase
        if self.punish_delay_response:
            self._Phases.append(PhaseSpec(
                phase_number=1,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: 1, port_details['target_ports']: 3},
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
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: 3, port_details['target_ports']:2},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay-stim',
                hz=hz,
                sounds_played=start_sound))
        else:
            self._Phases.append(PhaseSpec(
                phase_number=2,
                stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
                stimulus_update_fn=LickForReward.do_nothing_to_stim,
                stimulus_details=stimulus_details,
                transitions={do_nothing: None, port_details['target_ports']:2},
                frames_until_transition=delay_frame_num,
                auto_trigger=False,
                phase_type='stimulus',
                phase_name='delay-stim',
                hz=hz,
                sounds_played=start_sound))

        # reward phase spec
        self._Phases.append(RewardPhaseSpec(
            phase_number=3,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(self.itl),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=RandomSpurtsOfWater.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=reward_size,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=(station._sounds['reward_sound'], ms_reward_sound/1000.)),
            reward_valve='center_valve')

        # punishment phase spec
        self._Phases.append(PunishmentPhaseSpec(
            phase_number=4,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=(0,0,0,),autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=RandomSpurtsOfWater.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=ms_penalty,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='delay_phase',
            hz=hz,
            sounds_played=(station._sounds['punishment_sound'], ms_penalty_sound/1000.)),
            reward_valve='center_valve')

    def _simulate(self):
        station = StandardKeyboardStation()
        station.initialize()
        trial_record = {}
        quit = False
        while not Quit:
            trial_record,quit = self.do_trial(trial_record=trial_record,station=station,subject=None,compiled_record=None)
        station.close_window()

    def decache(self):
        self._Phases = dict()

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

    @staticmethod
    def trial_compiler(compiled_record,trial_record):
        print('at Gratings trial_compiler')

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardVisionBehaviorStation','StandardVisionHeadfixStation','StandardKeyboardStation']:
            return True
        else:
            return False

if __name__=='__main__':
    LFR = LickForReward('DefaultLFR')
    LFR._simulate()
