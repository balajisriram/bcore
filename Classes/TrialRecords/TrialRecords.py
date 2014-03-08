class TrialRecord(object):
    pass


class SessionRecord(object):

    data = []

    def __init__(self):
        pass

    def append(self, tR):
        self.data.append(tR)


class CompiledTrialRecord(object):

    def __init__(self):
        pass


class VisionBehaviorTrialRecord(TrialRecord):
    """
    """
    import time
    import datetime
    trialNumber = 0

    date = datetime.date.today()
    startTime = time.localtime()
    stopTime = None
    sessionNumber = None
    response = 0
    step = ''
    responseTime = 0
    phaseRecords = []

    protocolName = ''
    currentStep = ''
    numSteps = ''


class VisionBehaviorSessionRecord(SessionRecord):
    def __init__(self):
        import time
        self.sessionStartTime = time.localtime()
        self.data = []
        self.sessionEndTime = None

    def append(self, tR):
        self.data.append(tR)