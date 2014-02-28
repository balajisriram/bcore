from verlib import NormalizedVersion as Ver

class Protocol(object):
    pass
    
    
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
                trainingSteps   : list of tuples (stepNum,stepName,
                    criterionManager,sessionManager,trialManager,
                    reinforcementManager)
    """
    ver = Ver('0.0.1') #Feb 28 2014
    
    def __init__(self, **kwargs):
        self.name = kwargs['name']            
        self.trainingSteps = kwargs['trainingSteps']
        self.currentStep = 0
        
    def changeToStep(self, stepNum):
        self.currentStep = stepNum
        
    def getStep(self):
        return self.trainingSteps[self.currentStep]
        
    def getNumSteps(self):
        return len(self.trainingSteps)
     
        
class SequentialProtocol(Protocol):
    pass
    
class RandomizedProtocol(Protocol):