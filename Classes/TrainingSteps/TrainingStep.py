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

    def __init__(ts, **kwargs):
        ts.name = kwargs['name']
        ts.TrialManager = kwargs['trialManager']
        ts.Scheduler = kwargs['scheduler']
        ts.Criterion = kwargs['criterion']

    def scheduleOK(ts):
        return ts.Scheduler.scheduleOK()

    def doTrial(ts, **kwargs):
        # called by subject.doTrial()
        if __debug__:
            assert kwargs['session'].tsOKForSessMgr, ''

        tR = kwargs['trialRecords']

        tR.trialManagerName = ts.TrialManager.name
        tR.schedulerName = ts.Scheduler.name
        tR.criterionName = ts.Criterion.name

        tR.trialManagerClass = ts.TrialManager.__class__.__name__
        tR.schedulerClass = ts.Scheduler.__class__.__name__
        tR.criterionClass = ts.Criterion.__class__.__name__

        kwargs['trialManager'] = ts.TrialManager

        if ts.scheduleOK(**kwargs):
            tR = ts.TrialManager.doTrial(**kwargs)

        if ts.Criterion.graduate(**kwargs):
            kwargs['Graduate'] = True

        return tR
