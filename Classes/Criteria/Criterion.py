class Criterion(object):

    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def graduate(self, **kwargs):
        return False


class NumTrialsDoneCriterion(Criterion):

    def __init__(self, **kwargs):
        super(NumTrialsDoneCriterion, self).__init__(**kwargs)
        self.numTrials = kwargs['numTrials']
        self.numTrialsMode = 'global'
        if 'numTrialsMode' in kwargs:
            self.numTrialsMode = kwargs['numTrialsMode']
            # can be 'global' or 'consecutive'

    def graduate(self, **kwargs):
        cR = kwargs['compiled']
        # find the latest number of
        if self.numTrialsMode == 'consecutive':
            raise NotImplementedError()
        else:  # 'global'
            nT = [i for i in cR.trialNumber]
            raise NotImplementedError()
        if nT > self.numTrials:
            Graduate = True
        else:
            Graduate = False
        return Graduate


class PerformanceCriterion(Criterion):

    def __init__(self, **kwargs):
        super(PerformanceCriterion, self).__init__(**kwargs)
        self.pctCorrect = kwargs['pctCorrect']
        self.numTrials = kwargs['numTrials']

    def graduate(self, **kwargs):
        # find the latest number of
        if self.numTrialsMode == 'consecutive':
            pass
        Graduate = False
        return Graduate


class RateCriterion(Criterion):

    def __init__(self, **kwargs):
        super(PerformanceCriterion, self).__init__(**kwargs)
        self.trialsPerMin = kwargs['trialsPerMin']
        self.consecutiveMins = kwargs['consecutiveMins']

    def graduate(self, **kwargs):
        # find the latest number of
        if self.numTrialsMode == 'consecutive':
            pass
        Graduate = False
        return Graduate


class RepeatIndefinitely(Criterion):

    def __init__(self, **kwargs):
        super(RepeatIndefinitely, self).__init__(**kwargs)

    def graduate(self, **kwargs):
        return False