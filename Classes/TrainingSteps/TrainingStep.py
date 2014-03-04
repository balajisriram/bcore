class TrainingStep(object):
    """
        TRAININGSTEP is added to a protocol. This will determine the behavior
        of the step. All training steps will follow a trial structure and
        will need a trialManager. A Scheduler to determine when to show trials.
        And a Criterion to determine when to graduate.
    """
    name = ''
    TrialManager = []
    Scheduler = []
    Criterion = []

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.TrialManager = kwargs['trialManager']
        self.Scheduler = kwargs['scheduler']
        self.Criterion = kwargs['criterion']

    def doTrial(self, **kwargs):
        