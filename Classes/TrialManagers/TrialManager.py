from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

def compile_records(cR,tR):
    pass

class TrialManager(object):
    """
        TRIALMANAGER contains all the relevant details for managing
        trials. Currently very little is done here. All relevant details
        happens at StandardVisionBehaviorTrialManager
    """
    need_to_update = False
    _internal_objects = dict()
    ver = Ver('0.0.1')

    def __init__(self, name, **kwargs):
        self.name = name
        self.text_display = 'full'

    def do_trial(self, **kwargs):
        raise NotImplementedError('Abstract Class in TrialManager does\
            not implement doTrial()')

    def loop(self, **kwargs):
        pass
