__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class Criterion(object):

    def __init__(self, name='Unknown'):
        self.name = name

    def graduate(self, **kwargs):
        return False


class NumTrialsDoneCriterion(Criterion):

    def __init__(self, num_trials=100, num_trials_mode='global', name='Unknown'):
        super(NumTrialsDoneCriterion, self).__init__(name)
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def graduate(self, cR, **kwargs):
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
        self.pct_correct = pct_correct
        self.num_trials = num_trials
        self.num_trials_mode = num_trials_mode

    def graduate(self, cR, **kwargs):
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
        self.trials_per_minute = trials_per_minute
        self.consecutive_minutes = consecutive_minutes

    def graduate(self, **kwargs):
        Graduate = False
        raise NotImplementedError()
        return graduate


class RepeatIndefinitely(Criterion):

    def __init__(self, name='Unknown'):
        super(RepeatIndefinitely, self).__init__(name)

    def graduate(self, cR, **kwargs):
        return False