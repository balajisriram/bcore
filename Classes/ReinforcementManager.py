from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class ReinforcementManager(object):

    def __init__(self, name='DefaultReinforcementManager'):
        self.ver = Ver("0.0.1")
        
        self.name = name

    def __repr__(self):
        return "ReinforcementManager object with name:%s" % self.name


class NoReinforcement(ReinforcementManager):

    def __init__(self, name='NoReinforcement'):
        self.ver = Ver("0.0.1")

        super(NoReinforcement, self).__init__(name = name)

    def __repr__(self):
        return "NoReinforcement object"


class ConstantReinforcement(ReinforcementManager):

    def __init__(self,
                 reward_scalar = 1,
                 request_reward_scalar = 1,
                 penalty_scalar = 1,
                 fraction_reward_sound_in_on = 0,
                 fraction_penalty_sound_is_on = 0,
                 request_mode = 'first',
                 name = 'DefaultConstantReinforcement'):
        self.ver = Ver("0.0.1")
        super(ConstantReinforcement, self).__init__(name = name)
        self.reward_scalar = reward_scalar
        self.request_reward_scalar = request_reward_scalar
        self.penalty_scalar = penalty_scalar
        self.fraction_reward_sound_in_on = fraction_reward_sound_in_on
        self.fraction_penalty_sound_is_on = fraction_penalty_sound_is_on
        self.request_mode = request_mode

    def __repr__(self):
        return "ConstantReinforcement object"

    def calculate_reinforcement(self, subject, **kwargs):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_in_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound

        
class RandomReinforcement(ConstantReinforcement):

    def __init__(self,
                 probability = 0.01,
                 reward_scalar = 1,
                 request_reward_scalar = 1,
                 penalty_scalar = 1,
                 fraction_reward_sound_in_on = 0,
                 fraction_penalty_sound_is_on = 0,
                 request_mode = 'first',
                 name = 'DefaultRandomReinforcement'):
        self.ver = Ver("0.0.1")
        super(RandomReinforcement, self).__init__(name=name, reward_scalar=reward_scalar,
                                                  request_reward_scalar=request_reward_scalar,
                                                  penalty_scalar=penalty_scalar,
                                                  fraction_reward_sound_in_on=fraction_reward_sound_in_on,
                                                  fraction_penalty_sound_is_on=fraction_penalty_sound_is_on,
                                                  request_mode=request_mode)
        self.probability=probability
        assert self.probability>=0. and self.probability<=1., 'probability scalar between zero and one (inclusive)'

    def __repr__(self):
        return "RandomReinforcement object"

    def calculate_reinforcement(self, subject, **kwargs):
        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = 
            super(RandomReinforcement,self).calculate_reinforcement(self, subject, **kwargs)
        if np.random.rand()<self.probability:
            return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound
        else:
            return 0., 0., 0., 0., 0.

class RewardNCorrectInARow(ReinforcementManager):

    def __init__(self,
                 reward_scalar=1,
                 request_reward_scalar=1,
                 penalty_scalar=1,
                 fraction_reward_sound_in_on=0,
                 fraction_penalty_sound_is_on=0,
                 request_mode='first',
                 name='DefaultNCorrectReinforcement'):
        self.ver = Ver("0.0.1")
        super(RewardNCorrectInARow, self).__init__(name = name)
        self.reward_scalar = reward_scalar
        self.request_reward_scalar = request_reward_scalar
        self.penalty_scalar = penalty_scalar
        self.fraction_reward_sound_in_on = fraction_reward_sound_in_on
        self.fraction_penalty_sound_is_on = fraction_penalty_sound_is_on
        self.request_mode = request_mode

    def __repr__(self):
        return "RewardNCorrectInARow object"


    def calculate_reinforcement(self, subject):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_in_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound

