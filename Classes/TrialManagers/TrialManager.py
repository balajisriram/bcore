class TrialManager(object):
    """
        TRIALMANAGER contains all the relevant details for managing
        trials. Currently very little is done here. All relevant details
        happens at StandardVisionBehaviorTrialManager
    """
    name = ''
    textDisplay = 'full'

    needToUpdate = False

    def __init__(tm, **kwargs):
        if 'name' in kwargs:
            tm.name = kwargs['name']
        if 'textDisplay' in kwargs:
            tm.textDisplay = kwargs['textDisplay']
        assert tm.textDisplay in ['full','light','off'],\
            "textDisplay not one of ['full','light','off']"

    def doTrial(tm, **kwargs):
        raise NotImplementedError('Abstract Class in TrialManager does\
            not implement doTrial()')

    def loop(tm, **kwargs):
        pass
