__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class TrainingStep(object):
    """
        TRAININGSTEP is added to a protocol. This will determine the behavior
        of the step. All training steps will follow a trial structure and
        will need a trialManager. A Scheduler to determine when to show trials.
        And a Criterion to determine when to graduate.
    """
    name = ''
    trial_manager = []
    scheduler = []
    criterion = []

    def __init__(ts, name, trial_manager, scheduler, criterion, **kwargs):
        ts.name = name
        ts.trial_manager = trial_manager
        ts.scheduler = scheduler
        ts.criterion = criterion

    def schedule_ok(ts):
        return ts.scheduler.schedule_ok()

    def do_trial(ts, tR, **kwargs):
        # called by subject.doTrial()
        if __debug__:
            assert kwargs['session'].tsOKForSessMgr, ''

        tR.trial_manager_name = ts.trial_manager.name
        tR.scheduler_name = ts.scheduler.name
        tR.criterion_name = ts.criterion.name

        tR.trial_manager_class = ts.trial_manager.__class__.__name__
        tR.scheduler_class = ts.scheduler.__class__.__name__
        tR.criterion_class = ts.criterion.__class__.__name__

        tR.trial_manager_version_number = ts.trial_manager.ver
        tR.scheduler_version_number = ts.scheduler.ver
        tR.criterion_version_number = ts.criterion.ver

        if ts.schedule_ok(**kwargs):
            tR = ts.trial_manager.do_trial(tR, **kwargs)

        if ts.criterion.graduate(tR, **kwargs):
            tR.graduated_end_of_trial = True
        else:
            tR.graduated_end_of_trial = False

        return tR
