from verlib import NormalizedVersion as Ver
from .Criteria.Criterion import RepeatIndefinitely
from .SessionManager import NoTimeOff
from .TrialManagers.GratingsTrialManagers import Gratings
from .ReinforcementManager import NoReinforcement

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

###########################################################################
class TrainingStep(object):
    """
        TRAINING STEP contains the following information for each step
        name ::  nme of the step
        
    """
    ver = Ver('0.0.1')
    
    def __init__(self, name, criterion, session_manager, trial_manager, reinforcement_manager):
        self.name = name
        self.criterion=criterion
        self.session_manager=session_manager
        self.trial_manager=trial_manager
        self.reinforcement_manager=reinforcement_manager
        
    def do_trial(self, subject, station, trial_record, compiled_record, quit):
        graduate = False
        manual_ts_change = False
        
        try:
            keep_doing_trials, secs_remaining_to_state_flip = self.session_manager.check_schedule(subject=subject, trial_record=trial_record, compiled_record=compiled_record)
            if keep_doing_trials:
                stop_early, trial_record = self.trial_manager.do_trial(station=station, subject=subject, trial_record=trial_record, compiled_record=compiled_record)
                import pdb
                pdb.set_trace()
                graduate = self.criterion.check_criterion(subject=subject, trial_record=trial_record, compiled_record=compiled_record)
        except:
            station.close_session()
            
        
    
###########################################################################
# PROTOCOLS
###########################################################################
class Protocol(object):

    ver = Ver('0.0.1')  # Feb 28 2014

    def __init__(self, name='DefaultProtocol'):
        self.name = name

    @staticmethod
    def protocol_ok_for_session_manager(self, **kwargs):
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
    ver = Ver('0.0.1')  # Feb 28 2014

    def __init__(self, training_steps, name="DefaultSimpleProtocol"):
        super(SimpleProtocol, self).__init__(name = name)
        self.training_steps = training_steps
        self.current_step = 0

    def change_to_step(self, step_num):
        self.current_step = step_num

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
    ver = Ver('0.0.1')  # Feb 28 2014

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
    ver = Ver('0.0.1')  # Feb 28 2014

    def __init__(self, **kwargs):
        super(RandomizedProtocol, self).__init__(**kwargs)

    def change_to_step(self, step_num):
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


class DemoGratingsProtocol(SimpleProtocol):
    """
        DEMOGRATINGSPROTOCOL shows a simple Gratings stimulus
    """
    ver = Ver('0.0.1')  # Feb 28 2014

    def __init__(self):
        name = "DemoGratingsProtocol"
        training_steps = [TrainingStep(
        name="DemoGratingStepNum1", 
        criterion=RepeatIndefinitely(), 
        session_manager=NoTimeOff(), 
        trial_manager=Gratings(), 
        reinforcement_manager=NoReinforcement())]
        super(DemoGratingsProtocol,self).__init__(training_steps, name=name)