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

    # set in init
    date = datetime.date.today()
    startTime = time.localtime()

    # set in station
    trialNumber = 0
    sessionNumber = None
    stopTime = None
    resolution = None
    subjectsInStation = None

    # set in subject
    protocolName = ''
    currentStep = ''
    numSteps = ''
    criterionMet = False

    # set in trainingStep
    trialManagerName = ''
    schedulerName = ''
    criterionName = ''

    #set in trialManager
    response = 0
    step = ''
    responseTime = 0
    phaseRecords = []

    # set in stimManager
    stimRecords = []


class VisionBehaviorSessionRecord(SessionRecord):
    def __init__(self):
        import time
        self.sessionStartTime = time.localtime()
        self.data = []
        self.sessionEndTime = None

    def append(self, tR):
        self.data.append(tR)