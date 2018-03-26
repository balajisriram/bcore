from verlib import NormalizedVersion as Ver

__author__ = 'Balaji Sriram'


class ReinforcementManager(object):
    ver = Ver('0.0.1')

    def __init__(self, name='DefaultReinforcementManager'):
        self.name = name


class ConstantReinforcement(ReinforcementManager):
    ver = Ver('0.0.1')

    def __init__(self,
                 reward_scalar = 1,
                 request_reward_scalar = 1,
                 penalty_scalar = 1,
                 fraction_reward_sound_in_on = 0,
                 fraction_penalty_sound_is_on = 0,
                 request_mode = 'first',
                 name = 'DefaultConstantReinforcement'):
        super(ConstantReinforcement, self).__init__(name = name)
        self.reward_scalar = reward_scalar
        self.request_reward_scalar = request_reward_scalar
        self.penalty_scalar = penalty_scalar
        self.fraction_reward_sound_in_on = fraction_reward_sound_in_on
        self.fraction_penalty_sound_is_on = fraction_penalty_sound_is_on
        self.request_mode = request_mode

    def calculate_reinforcement(self, subject):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_in_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound


class RewardNCorrectInARow(ReinforcementManager):
    ver = Ver('0.0.1')

    def __init__(self,
                 reward_scalar = 1,
                 request_reward_scalar = 1,
                 penalty_scalar = 1,
                 fraction_reward_sound_in_on = 0,
                 fraction_penalty_sound_is_on = 0,
                 request_mode = 'first',
                 name = 'DefaultNCorrectReinforcement'):
        super(RewardNCorrectInARow, self).__init__(name = name)
        self.reward_scalar = reward_scalar
        self.request_reward_scalar = request_reward_scalar
        self.penalty_scalar = penalty_scalar
        self.fraction_reward_sound_in_on = fraction_reward_sound_in_on
        self.fraction_penalty_sound_is_on = fraction_penalty_sound_is_on
        self.request_mode = request_mode

    def calculate_reinforcement(self, subject):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_in_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound

