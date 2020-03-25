from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"


class SessionManager(object):
    sessionmgr_version = Ver('0.0.1')
    name = ''
    def __init__(self, **kwargs):
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.sessionmgr_version = Ver(data['sessionmgr_version'])
        self.name = data['name']

    def save_to_dict(self):
        data = dict()
        data['sessionmgr_version'] = self.sessionmgr_version.__str__()
        data['name'] = self.name
        return data

    def __repr__(self):
        return "SessionManager object with name:%s" %(self.name)

    def check_schedule(self):
        return False


class NoTimeOff(SessionManager):
    notimeoff_version = Ver('0.0.1')
    def __init__(self, **kwargs):
        super(NoTimeOff,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.notimeoff_version = Ver(data['notimeoff_version'])

    def save_to_dict(self):
        data = super(NoTimeOff,self).save_to_dict()
        data['notimeoff_version'] = self.notimeoff_version.__str__()
        return data

    def __repr__(self):
        return "NoTimeOff object"

    def check_schedule(self, **kwargs):
        # Returns keep_doing_trials, secs_remaining_until_state_flip
        keep_doing_trials = True
        secs_remaining_until_state_flip = 0
        return keep_doing_trials, secs_remaining_until_state_flip


class MinutesPerSession(SessionManager):
    minutespersession_version = Ver('0.0.1')
    minutes = None
    hours_between_sessions = None
    def __init__(self, **kwargs):
        super(MinutesPerSession,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.minutespersession_version = Ver(data['minutespersession_version'])
        self.minutes = data['minutes']
        self.hours_between_sessions = data['hours_between_sessions']

    def save_to_dict(self):
        data = super(MinutesPerSession,self).save_to_dict()
        data['minutespersession_version'] = self.minutespersession_version.__str__()
        data['minutes'] = self.minutes
        data['hours_between_sessions'] = self.hours_between_sessions
        return data

    def __repr__(self):
        return "MinutesPerSession object, %s minutes with %s hrs between sessions" %(self.minutes, self.hours_between_sessions)

    def check_schedule(self):
        return NotImplementedError()


class TimeRange(SessionManager):
    timerange_version = Ver('0.0.1')
    time_start = None
    time_stop = None
    def __init__(self, **kwargs):
        super(TimeRange,self).__init__(**kwargs)
        if not kwargs:
            pass
        elif 'data' in kwargs:
            self = self.load_from_dict(kwargs['data]'])
        else:
            pass

    def load_from_dict(self,data):
        self.timerange_version = Ver(data['timerange_version'])
        self.time_start = data['time_start']
        self.time_stop = data['time_stop']

    def save_to_dict(self):
        data = super(TimeRange,self).save_to_dict()
        data['timerange_version'] = self.timerange_version.__str__()
        data['time_start'] = self.time_start
        data['time_stop'] = self.time_stop
        return data

    def __repr__(self):
        return "TimeRange object"

    def check_schedule(self):
        return NotImplementedError()
        