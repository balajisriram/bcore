from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class Criterion(object):

    def __init__(self, name='Unknown'):
        self.name = name
        self.ver = Ver('0.0.1')

    def check_criterion(self, **kwargs):
        return False


class NumTrialsDoneCriterion(Criterion):

    def __init__(self, num_trials=100, num_trials_mode='global', name='Unknown'):
        super(NumTrialsDoneCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def check_criterion(self, cR, **kwargs):
        # find the latest number of
        if self.num_trials_mode == 'consecutive':
            raise NotImplementedError()
        else:  # 'global'
            nT = [i for i in cR.trial_number]
            raise NotImplementedError()
        if nT > self.num_trials:
            graduate = True
        else:
            graduate = False

        return graduate


class PerformanceCriterion(Criterion):

    def __init__(self, pct_correct=0.8, num_trials=200, num_trials_mode='global', name='Unknown'):
        super(PerformanceCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.pct_correct = pct_correct
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def check_criterion(self, cR, **kwargs):
        # find the latest number of
        if self.num_trials_mode == 'consecutive':
            pass
            raise NotImplementedError()
        else:
            raise NotImplementedError()

        graduate = False
        return graduate


class RateCriterion(Criterion):

    def __init__(self, trials_per_minute=10, consecutive_minutes=5, name='Unknown'):
        super(PerformanceCriterion, self).__init__(name)
        self.ver = Ver('0.0.1')
        self.trials_per_minute = trials_per_minute
        self.consecutive_minutes = consecutive_minutes

    def check_criterion(self, **kwargs):
        Graduate = False
        raise NotImplementedError()
        return graduate


class RepeatIndefinitely(Criterion):

    def __init__(self, name='Unknown'):
        self.ver = Ver('0.0.1')
        super(RepeatIndefinitely, self).__init__(name)

    def check_criterion(self, **kwargs):
        return False