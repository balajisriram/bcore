from verlib import NormalizedVersion as Ver
import numpy as np

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class ReinforcementManager(object):
    reinfmgr_version = Ver('0.0.1')
    name = ''

    def __init__(self, **kwargs):
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self,data):
        self.reinfmgr_version = Ver(data['reinfmgr_version'])
        self.name = data['name']
        return self

    def save_to_dict(self):
        data = dict()
        data['reinfmgr_version'] = self.reinfmgr_version.__str__()
        data['name'] = self.name
        return data

    def __repr__(self):
        return "ReinforcementManager object with name:%s" % self.name


class NoReinforcement(ReinforcementManager):
    noreinforcement_version = Ver('0.0.1')
    
    def __init__(self, **kwargs):
        super(NoReinforcement,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self,data):
        self.noreinforcement_version = Ver(data['noreinforcement_version'])
        return self

    def save_to_dict(self):
        data = super(NoReinforcement,self).save_to_dict()
        data['noreinforcement_version'] = self.noreinforcement_version.__str__()
        return data

    def __repr__(self):
        return "NoReinforcement object"

    def calculate_reinforcement(self, subject, **kwargs):
        reward_size = 0
        request_reward_size = 0
        ms_penalty = 0
        ms_reward_sound = 0
        ms_penalty_sound = 0

        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound


class ConstantReinforcement(ReinforcementManager):
    """
        VERSION HISTORY:
        0.0.1: Started out
        0.0.2: fraction_reward_sound_is_on was incorrectly named. Changed
    """
    constantreinf_version = Ver('0.0.2')
    reward_scalar = None 
    request_reward_scalar = None 
    penalty_scalar = None
    fraction_reward_sound_is_on = None
    fraction_penalty_sound_is_on = None
    request_mode = ''

    def __init__(self, , **kwargs):
        super(ConstantReinforcement,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self,data):
        self.constantreinf_version = Ver(data['constantreinf_version'])
        self.reward_scalar = data['reward_scalar']
        self.request_reward_scalar = data['request_reward_scalar']
        self.penalty_scalar = data['penalty_scalar']
        self.fraction_reward_sound_is_on = data['fraction_reward_sound_is_on']
        self.fraction_penalty_sound_is_on = data['fraction_penalty_sound_is_on']
        self.request_mode = data['request_mode']
        return self

    def save_to_dict(self):
        data = super(ConstantReinforcement,self).save_to_dict()
        data['constantreinf_version'] = self.constantreinf_version.__str__()
        data['reward_scalar'] = self.reward_scalar
        data['request_reward_scalar'] = self.request_reward_scalar
        data['penalty_scalar'] = self.penalty_scalar
        data['fraction_reward_sound_is_on'] = self.fraction_reward_sound_is_on
        data['fraction_penalty_sound_is_on'] = self.fraction_penalty_sound_is_on
        data['request_mode'] = self.request_mode
        return data

    def __repr__(self):
        return "ConstantReinforcement object"

    def calculate_reinforcement(self, subject, **kwargs):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_is_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound


class RandomReinforcement(ConstantReinforcement):

    randomreinf_version = Ver('0.0.1')
    probability = None

    def __init__(self, **kwargs):
        super(RandomReinforcement,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.randomreinf_version = Ver(data['randomreinf_version'])
        self.probability = data['probability']
        return self

    def save_to_dict(self):
        data = super(RandomReinforcement,self).save_to_dict()
        data['randomreinf_version'] = self.randomreinf_version.__str__()
        data['probability'] = self.probability
        return data

    def __repr__(self):
        return "RandomReinforcement object"

    def calculate_reinforcement(self, subject, **kwargs):
        reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound = super(RandomReinforcement,self).calculate_reinforcement(subject=subject)
        if np.random.rand()<self.probability:
            return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound
        else:
            return 0., 0., 0., 0., 0.

class RewardNCorrectInARow(ReinforcementManager):

    rewardncorrect_version = Ver('0.0.1')
    n_correct = None 
    _current_n = 0

    def __init__(self, **kwargs):
        super(RewardNCorrectInARow,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data'])
        else:
            pass

    def load_from_dict(self, data):
        self.rewardncorrect_version = Ver(data['rewardncorrect_version'])
        self.n_correct = data['n_correct']
        return self

    def save_to_dict(self):
        data = super(RewardNCorrectInARow,self).save_to_dict()
        data['rewardncorrect_version'] = self.rewardncorrect_version.__str__()
        data['n_correct'] = self.n_correct
        return data

    def __repr__(self):
        return "RewardNCorrectInARow object"


    def calculate_reinforcement(self, subject, **kwargs):
        reward_size = subject.reward *self.reward_scalar
        request_reward_size = subject.reward*self.request_reward_scalar
        ms_penalty = subject.timeout*self.penalty_scalar
        ms_reward_sound = reward_size*self.fraction_reward_sound_is_on
        ms_penalty_sound = ms_penalty*self.fraction_penalty_sound_is_on

        update_rm = False
        return reward_size, request_reward_size, ms_penalty, ms_reward_sound, ms_penalty_sound
