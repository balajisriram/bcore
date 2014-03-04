import datetime
import time


class TrialManager(object):
    """
        TRIALMANAGER contains all the relevant details for managing
        trials. Currently very little is done here. All relevant details
        happens at StandardVisionBehaviorTrialManager
    """
    name = ''
    textDisplay = 'full'

    def __init__(tm, **kwargs):
        tm.name = kwargs['name']
        if 'textDisplay' in kwargs:
            tm.textDisplay = kwargs['textDisplay']

    def doTrial(tm, **kwargs):
        raise NotImplementedError('Abstract Class in TrialManager does\
            not implement doTrial()')

    def loop(tm, **kwargs):
        pass


class TrialRecord(object):
    trialNumber = 0
    date = datetime.date.today()
    startTime = time.localtime()
    stopTime = None
    sessionNumber = None


class SessionRecord(object):
    pass


class CompiledTrialRecord(object):
    pass