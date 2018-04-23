from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class Protocol(object):

    ver = Ver('0.0.1')  # Feb 28 2014
    name = ''

    def __init__(self, **kwargs):
        self.name = kwargs['name']

    def ProtocolOKForSessionMgr(self, **kwargs):
        return False


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
    training_steps = []
    current_step = 0

    def __init__(self, **kwargs):
        super(SimpleProtocol, self).__init__(**kwargs)
        self.training_steps = kwargs['training_steps']
        self.current_step = 0

    def change_to_step(self, stepNum):
        self.current_step = stepNum

    def step(self):
        return self.training_steps[self.current_step]

    def num_steps(self):
        return len(self.training_steps)

    def add_step(self, step):
        self.training_steps.append(step)


class SequentialProtocol(SimpleProtocol):
    """
        SEQUENTIALPROTOCOL is a SIMPLEPROTOCOL that only allows for graduate
        and degraduate function with the change_to_step function erroring
    """
    def __init__(self, **kwargs):
        super(SequentialProtocol, self).__init__(**kwargs)

    def graduate(self, safe=False):
        self.current_step += 1
        if safe and self.current_step == self.num_steps():
            self.current_step -= 1

    def fallback(self, safe=False):
        self.current_step -= 1
        if safe and self.current_step < 0:
            self.current_step -= 0

    def change_to_step(self, step_num):
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

    def graduate(self, ensure_different=False):
        import random
        if not ensure_different:
            self.current_step = random.randint(0, self.num_steps() - 1)
        else:
            current_step = self.current_step
            new_step = current_step
            while current_step == new_step:
                new_step = random.randint(0, self.num_steps() - 1)
            self.current_step = new_step