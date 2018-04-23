__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class TrialManager(object):
    """
        TRIALMANAGER contains all the relevant details for managing
        trials. Currently very little is done here. All relevant details
        happens at StandardVisionBehaviorTrialManager
    """
    name = ''
    text_display = 'full'

    need_to_update = False

    _internal_objects = dict()

    def __init__(self, name, **kwargs):
        self.name = name


    def do_trial(self, **kwargs):
        raise NotImplementedError('Abstract Class in TrialManager does\
            not implement doTrial()')

    def loop(self, **kwargs):
        pass

    def decache(self):
        self._internal_objects = dict()