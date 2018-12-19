__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

from BCore.Classes.Protocol import SequentialProtocol, TrainingStep
from BCore.Classes.Criterion import RepeatIndefinitely, NumTrialsDoneCriterion, PerformanceCriterion
from BCore.Classes.SessionManager import NoTimeOff
from BCore.Classes.TrialManagers.NoStimulusTrialManagers import LickForReward, ClassicalConditioning, AuditoryGoOnly
from BCore.Classes.ReinforcementManager import ConstantReinforcement


def get_lick_for_reward_protocol():
    training_steps = [TrainingStep(name='lick_for_reward_with_autoreward_no_penalty',
                                    trial_manager=LickForReward(name='lick_for_reward_with_autoreward_no_penalty_Rand_',
                                                 reinforcement_manager=ConstantReinforcement(fraction_reward_sound_in_on=1,fraction_penalty_sound_is_on=0.1),
                                                 trial_start_sound_on = True,
                                                 delay_distribution = ('Gaussian',[9,4]),
                                                 punish_delay_response = False,
                                                 response_duration = 1.,
                                                 auto_reward = True,
                                                 punish_misses = False,),
                                    session_manager=NoTimeOff(),
                                    criterion=NumTrialsDoneCriterion(num_trials=100, num_trials_mode='consecutive',)),
                      TrainingStep(name='lick_for_reward_no_delay_penalty_no_autoreward_no_miss_penalty',
                                    trial_manager=LickForReward(name='lick_for_reward_no_delay_penalty_no_autoreward_no_miss_penalty',
                                                 reinforcement_manager=ConstantReinforcement(fraction_reward_sound_in_on=1,fraction_penalty_sound_is_on=0.1),
                                                 trial_start_sound_on = True,
                                                 delay_distribution = ('Gaussian',[9,4]),
                                                 punish_delay_response = False,
                                                 response_duration = 1.,
                                                 auto_reward = False,
                                                 punish_misses = False,),
                                    session_manager=NoTimeOff(),
                                    criterion=NumTrialsDoneCriterion(num_trials=500, num_trials_mode='consecutive',)),
                      TrainingStep(name='lick_for_reward_with_delay_penalty',
                                    trial_manager=LickForReward(name='lick_for_reward_with_penalty',
                                                 reinforcement_manager=ConstantReinforcement(fraction_reward_sound_in_on=1,fraction_penalty_sound_is_on=0.1),
                                                 trial_start_sound_on = True,
                                                 delay_distribution = ('Gaussian',[9,4]),
                                                 punish_delay_response = True,
                                                 response_duration = 1.,
                                                 auto_reward = False,
                                                 punish_misses = False,),
                                    session_manager=NoTimeOff(),
                                    criterion=PerformanceCriterion(num_trials_mode='consecutive',num_trials=200,pct_correct=0.8)),]

    return SequentialProtocol(training_steps=training_steps, name='lick_for_reward_biogen_09142018')

def get_classical_conditioning_protocol():
    training_steps = [TrainingStep(name='classical_conditioning_notimeoff_repeatindefinitely',
                                    trial_manager=ClassicalConditioning(name='StandardClassicalConditioning',
                                                 reinforcement_manager=ConstantReinforcement(fraction_reward_sound_in_on=1,fraction_penalty_sound_is_on=0.1),
                                                 delay_distribution = ('Gaussian',[9,4]),
                                                 punish_delay_response = False,
                                                 response_duration = 2.,),
                                    session_manager=NoTimeOff(),
                                    criterion=RepeatIndefinitely()),]

    return SequentialProtocol(training_steps=training_steps, name='classical_conditioning_12022018')

def get_auditory_go_protocol():
    training_steps = [TrainingStep(name='auditory_go_notimeoff_repeatindefinitely',
                                    trial_manager=AuditoryGoOnly(name='AuditoryGoOnly_12192018',
                                                 reinforcement_manager=ConstantReinforcement(fraction_reward_sound_in_on=1,fraction_penalty_sound_is_on=0.1),
                                                 delay_distribution = ('Gaussian',[9,4]),
                                                 response_duration = 2.,),
                                    session_manager=NoTimeOff(),
                                    criterion=RepeatIndefinitely()),]
    return SequentialProtocol(training_steps=training_steps, name='auditory_go_12192018')

def get_behavior_protocol_biogen(name='lick_for_reward_biogen_09142018'):
    if name in ['lick_for_reward_biogen_09142018']:
        return get_lick_for_reward_protocol()
    elif name in ['classical_conditioning_protocol_12022018','ccp']:
        return get_classical_conditioning_protocol()
    elif name in ['auditory_go_protocol_12192018','audgo']:
        return get_auditory_go_protocol()
