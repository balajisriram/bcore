from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class SessionManager(object):

    def __init__(self, name='Unknown', **kwargs):
        self.ver = Ver('0.0.1')
        self.name = name

    def __repr__(self):
        return "SessionManager object with name:%s" %(self.name)

    def check_schedule(self):
        return False


class NoTimeOff(SessionManager):

    def __init__(self, name='DefaultNoTimeOff', **kwargs):
        self.ver = Ver('0.0.1')
        super(NoTimeOff, self).__init__(name=name, **kwargs)

    def __repr__(self):
        return "NoTimeOff object"

    def check_schedule(self, **kwargs):
        # Returns keep_doing_trials, secs_remaining_until_state_flip
        keep_doing_trials = True
        secs_remaining_until_state_flip = 0
        return keep_doing_trials, secs_remaining_until_state_flip


class MinutesPerSession(SessionManager):

    def __init__(self, name='DefaultMinutesPerSession', minutes = 60, hours_between_sessions = 23, **kwargs):
        self.ver = Ver('0.0.1')
        super(MinutesPerSession, self).__init__(name=name, **kwargs)
        self.minutes = minutes
        self.hours_between_sessions = hours_between_sessions

    def __repr__(self):
        return "MinutesPerSession object, %s minutes with %s hrs between sessions" %(self.minutes, self.hours_between_sessions)

    def check_schedule(self):
        return NotImplementedError()


class TimeRange(SessionManager):

    def __init__(self, name='DefaultHourRange',time_start=0, time_stop=1, **kwargs):
        self.ver = Ver('0.0.1')
        super(TimeRange, self).__init__(name=name, **kwargs)
        self.time_start = time_start
        self.time_stop = time_stop

    def __repr__(self):
        return "TimeRange object"

    def check_schedule(self):
        return NotImplementedError()
        