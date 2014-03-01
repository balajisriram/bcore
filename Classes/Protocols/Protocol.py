from verlib import NormalizedVersion as Ver


class Protocol(object):

    ver = Ver('0.0.1')  # Feb 28 2014
    name = ''

    def __init__(self, **kwargs):
        self.name = kwargs['name']


class MetaProtocol(Protocol):
    """
        METAPROTOCOL in my vision contains other protocols in
        its trainingSteps and asks for the right steps at the
        right time. The use case for this is as follows:

        - I get subjects from naive to trained on some task
        or sequence of tasks. This is the 'training' phase.
        - Past the training stage, I test subjects in the
        'testing' phase on some subset of the tasks.
        - And the questions I want to ask is whether randomized
        training/testing was a better method than sequential
        training/testing or some combination of the two?
    """
    pass


class SimpleProtocol(Protocol):
    """
        SIMPLEPROTOCOL contains a list of training steps and
        allows change in steps
                name            : stringIdentifier
                trainingSteps   : list of tuples (stepName,
                    criterionManager,sessionManager,trialManager,
                    reinforcementManager)
    """
    trainingSteps = []
    currentStep = 0

    def __init__(self, **kwargs):
        super(SimpleProtocol, self).__init__(**kwargs)
        self.trainingSteps = kwargs['trainingSteps']
        self.currentStep = 0

    def changeToStep(self, stepNum):
        self.currentStep = stepNum

    def step(self):
        return self.trainingSteps[self.currentStep]

    def numSteps(self):
        return len(self.trainingSteps)


class SequentialProtocol(SimpleProtocol):
    """
        SEQUENTIALPROTOCOL is a SIMPLEPROTOCOL that only allows for graduate
        and degraduate function with the changeToStep function erroring
    """
    def __init__(self, **kwargs):
        super(SequentialProtocol, self).__init__(**kwargs)

    def graduate(self, safe=False):
        self.currentStep += 1
        if safe and self.currentStep == self.numSteps():
            self.currentStep -= 1

    def fallback(self, safe=False):
        self.currentStep -= 1
        if safe and self.currentStep < 0:
            self.currentStep -= 0

    def changeToStep(self, stepNum):
        raise NotImplementedError('SequentialProtocol does not allow arbitrary\
        step changes. Use graduate() and fallback() only')


class RandomizedProtocol(SimpleProtocol):
    """
        RANDOMIZEDPROTOCOL is a SIMPLEPROTOCOL
    """
    def __init__(self, **kwargs):
        super(RandomizedProtocol, self).__init__(**kwargs)

    def changeToStep(self, stepNum):
        raise NotImplementedError('RandomizedProtocol does not allow arbitrary\
        step changes. Use graduate() only')

    def graduate(self, ensureDifferent=False):
        import random
        if not ensureDifferent:
            self.currentStep = random.randint(0, self.numSteps() - 1)
        else:
            currentStep = self.currentStep
            newStep = currentStep
            while currentStep == newStep:
                newStep = random.randint(0, self.numSteps() - 1)
            self.currentStep = newStep