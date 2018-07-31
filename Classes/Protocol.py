from verlib import NormalizedVersion as Ver
from .Criteria.Criterion import RepeatIndefinitely
from .SessionManager import NoTimeOff
from .TrialManagers.GratingsTrialManagers import Gratings,AFCGratings
from .ReinforcementManager import NoReinforcement,ConstantReinforcement
import psychopy
import traceback

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
        TRAININGSTEP is added to a protocol. This will determine the behavior
        of the step. All training steps will follow a trial structure and
        will need a trialManager. A SessionManager to determine when to show trials.
        And a Criterion to determine when to graduate.
    """

    def __init__(self, name, trial_manager, session_manager, criterion):
        self.ver = Ver('0.0.1')
        self.name = name
        self.trial_manager = trial_manager
        self.session_manager = session_manager
        self.criterion = criterion

    def do_trial(self,subject,station, trial_record,compiled_record,quit):
        graduate = False
        manual_ts_change = False
        # self,subject,station, trial_record,compiled_record,quit
        # called by subject.doTrial()
        if __debug__:
            pass
        trial_record['trial_manager_name'] = self.trial_manager.name
        trial_record['session_manager_name'] = self.session_manager.name
        trial_record['criterion_name'] = self.criterion.name

        trial_record['trial_manager_class'] = self.trial_manager.__class__.__name__
        trial_record['session_manager_class'] = self.session_manager.__class__.__name__
        trial_record['criterion_class'] = self.criterion.__class__.__name__

        trial_record['trial_manager_version_number'] = self.trial_manager.ver.__str__()
        trial_record['session_manager_version_number'] = self.session_manager.ver.__str__()
        trial_record['criterion_version_number'] = self.criterion.ver.__str__()
        
        trial_record['graduate'] = False
        try:
            keep_doing_trials, secs_remaining_to_state_flip = self.session_manager.check_schedule(subject=subject, trial_record=trial_record, compiled_record=compiled_record)
            
            if keep_doing_trials:
                trial_record,quit = self.trial_manager.do_trial(station=station,subject=subject,trial_record=trial_record,compiled_record=compiled_record,quit=quit)
            else:
                psychopy.core.wait(secs_remaining_to_state_flip/2.,hogCPUperiod=0.1)
            
            graduate = self.criterion.check_criterion(subject=subject, trial_record=trial_record, compiled_record=compiled_record, station = station)
            if graduate:
                trial_record['graduate'] = True
        except Exception as e:
            traceback.print_exc()
            print("type error: " + str(e))
            station.close_session() # should this be here?
        return trial_record,quit
        
###########################################################################
# PROTOCOLS
###########################################################################
class Protocol(object):

    def __init__(self, name='DefaultProtocol'):
        self.ver = Ver('0.0.1')  # Feb 28 2014
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

    def __init__(self, training_steps, name="DefaultSimpleProtocol"):
        self.ver = Ver('0.0.1')  # Feb 28 2014
        super(SimpleProtocol, self).__init__(name = name)
        self.training_steps = training_steps
        self.current_step = 0

    def change_to_step(self, step_num):
        self.current_step = step_num

    def step(self, **kwargs):
        return self.training_steps[self.current_step]

    def num_steps(self):
        return len(self.training_steps)

    def add_step(self, step):
        self.training_steps.append(step)


class StartsAtOneProtocol(SimpleProtocol):
    """
        STARTSATONEPROTOCOL contains a list of training steps and
        allows change in steps. But dstarts at step 1 beginning of each day
                name            : stringIdentifier
                trainingSteps   : list of tuples (stepName,
                    criterionManager,sessionManager,trialManager,
                    reinforcementManager)
    """

    def __init__(self, training_steps, name="DefaultSimpleProtocol"):
        self.ver = Ver('0.0.1')  # Feb 28 2014
        super(SimpleProtocol, self).__init__(name = name)
        self.training_steps = training_steps
        self.current_step = 0

    def change_to_step(self, step_num):
        self.current_step = step_num

    def step(self, compiled_record):
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
        self.ver = Ver('0.0.1')
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
        self.ver = Ver('0.0.1')  # Feb 28 2014
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

    def __init__(self):
        self.ver = Ver('0.0.1')  # Feb 28 2014
        name = "DemoGratingsProtocol"
        training_steps = [TrainingStep(
        name="DemoGratingStepNum1", 
        trial_manager=AFCGratings(name='DemoAFCGratingsTrialManager',deg_per_cycs={'L':[0.20],'R':[0.20]},durations = {'L':[1.],'R':[1.]},reinforcement_manager=ConstantReinforcement()), 
        session_manager=NoTimeOff(), 
        criterion=RepeatIndefinitely())]
        super(DemoGratingsProtocol,self).__init__(training_steps, name=name)