from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class SessionManager(object):

    ver = Ver('0.0.1')

    def __init__(self, name='Unknown', **kwargs):
        self.name = name

    def check_schedule(self):
        return False


class NoTimeOff(SessionManager):
    ver = Ver('0.0.1')

    def __init__(self, name='DefaultNoTimeOff', **kwargs):
        super(NoTimeOff,self).__init__(name, **kwargs)

    def check_schedule(self):
        return True


class MinutesPerSession(SessionManager):
    ver = Ver('0.0.1')

    def __init__(self, name='DefaultMinutesPerSession', minutes = 60, hours_between_sessions = 23, **kwargs):
        super(MinutesPerSession, self).__init__(name, **kwargs)
        self.minutes = minutes
        self.hours_between_sessions = hours_between_sessions

    def check_schedule(self):
        return True