from verlib import NormalizedVersion as Ver

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

    def __init__(self, name, trial_manager, scheduler, criterion, **kwargs):
        self.ver = Ver('0.0.1')
        self.name = name
        self.trial_manager = trial_manager
        self.scheduler = scheduler
        self.criterion = criterion

    def schedule_ok(self):
        return self.scheduler.schedule_ok()

    def do_trial(self,subject,station, trial_record,compiled_record,quit):
        # self,subject,station, trial_record,compiled_record,quit
        # called by subject.doTrial()
        if __debug__:
            assert kwargs['session'].tsOKForSessMgr, ''

        trial_record['trial_manager_name'] = self.trial_manager.name
        trial_record['scheduler_name'] = self.scheduler.name
        trial_record['criterion_name'] = self.criterion.name

        trial_record['trial_manager_class'] = self.trial_manager.__class__.__name__
        trial_record['scheduler_class'] = self.scheduler.__class__.__name__
        trial_record['criterion_class'] = self.criterion.__class__.__name__

        trial_record['trial_manager_version_number'] = self.trial_manager.ver
        trial_record['scheduler_version_number'] = self.scheduler.ver
        trial_record['criterion_version_number'] = self.criterion.ver
        import pdb
        pdb.set_trace()

        if self.schedule_ok(**kwargs):
            trial_record,quit = self.trial_manager.do_trial(station=station,subject=subject,trial_record=trial_record,compiled_record=compiled_record,Quit=quit)

        if self.criterion.graduate(tR, **kwargs):
            tR.graduated_end_of_trial = True
        else:
            tR.graduated_end_of_trial = False

        return tR,quit