from verlib import NormalizedVersion as Ver
from BCore.Classes.TrialManagers.PhaseSpec import PhaseSpec,RewardPhaseSpec,PunishmentPhaseSpec,StimPhaseSpec
from BCore.Classes.TrialManagers.BaseTrialManagers import BaseTrialManager
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

################################# CLASSICALCONDITIONING ##################################
class ClassicalConditioning(BaseTrialManager):
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
                 response_duration = 2.,
                 iti=1.,
                 itl=(0.,0.,0.,),**kwargs):

        super(ClassicalConditioning,self).__init__(iti=iti, itl=itl)
        self.ver = Ver('0.0.2')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.delay_distribution = delay_distribution
        self.go_signal = go_signal
        self.response_duration = response_duration

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
            phase_number=0,
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
            phase_number=1,
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
            phase_number=2,
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

        if not self.station_ok_for_tm(station):
            print('CLASSICALCONDITIONING:DO_TRIAL:Station not ok for TM')
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        
        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        trial_record,quit = super(ClassicalConditioning,self).do_trial(station=station, subject=subject, trial_record=trial_record, compiled_record=compiled_record, quit=quit)
        return trial_record,quit

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardKeyboardStation','StandardVisionHeadfixStation']:
            return True
        else:
            return False


class AuditoryGoOnly(BaseTrialManager):
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
                 response_duration = 2.,
                 iti=1.,
                 itl=(0.,0.,0.,),**kwargs):
        super(AuditoryGoOnly,self).__init__(iti=iti, itl=itl)
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.delay_distribution = delay_distribution
        self.go_signal = go_signal
        self.response_duration = response_duration

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
            phase_number=0,
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
            phase_number=1,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_update_fn=BaseTrialManager.do_nothing_to_stim,
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
            phase_number=2,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=BaseTrialManager.do_nothing_to_stim,
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
            phase_number=3,
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
            phase_number=4,
            stimulus=psychopy.visual.Rect(win=station._window,width=station._window.size[0],height=station._window.size[1],fillColor=self.itl,autoLog=False),
            stimulus_details=None,
            stimulus_update_fn=BaseTrialManager.do_nothing_to_stim,
            transitions=None,
            frames_until_transition=iti_size,
            auto_trigger=False,
            phase_type='inter-trial',
            phase_name='iti_phase',
            hz=hz,
            sounds_played=None))

    def do_trial(self, station, subject, trial_record, compiled_record,quit):
        # returns quit and trial_record
        # resetup the window according to the itl

        # check if okay to run the trial manager with the station

        """
            TODO: should running port be part of the logic??
        """
        if not self.station_ok_for_tm(station):
            quit = True
            trial_record['correct'] = None
            trial_record['errored_out'] = True
            return trial_record,quit

        ## _setup_phases
        self._setup_phases(trial_record=trial_record, station=station,compiled_record=compiled_record, subject=subject)
        station._key_pressed = []

        trial_record,quit = super(AuditoryGoOnly,self).do_trial(station=station, subject=subject, trial_record=trial_record, compiled_record=compiled_record, quit=quit)
        return trial_record,quit

    @staticmethod
    def station_ok_for_tm(station):
        if station.__class__.__name__ in ['StandardKeyboardStation','StandardVisionHeadfixStation']:
            return True
        else:
            return False


##################################### RUN FOR REWARD #####################################
class RunForReward(BaseTrialManager):
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
                 iti=1., 
                 itl=(0.,0.,0.,),
                 **kwargs):
        super(RunForReward,self).__init__(iti=iti, itl=itl)
        self.ver = Ver('0.0.1')
        self.reinforcement_manager = reinforcement_manager
        self.name = name
        self.run_speed = run_speed
        self.run_duration_distribution = delay_distribution


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
