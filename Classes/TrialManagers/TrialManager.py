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

    def doTrial(tm, **kwargs):
        raise NotImplementedError('Abstract Class in TrialManager does\
            not implement doTrial()')

    def loop(tm, **kwargs):
        pass
