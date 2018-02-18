class SessionManager(object):

	ver = Ver('0.0.1')  # Feb 28 2014
	name = ''


	def __init__(self, name='Unknown', **kwargs):
		self.name = name

	def checkSchedule(self):
		return False
    


class NoTimeOff(SessionManager):

	# no new properties defined here

	def __init__(self, name='DefaultNoTimeOff', **kwargs):
		super(NoTimeOff,self).__init__(name, **kwargs)

	def checkSchedule(self):
		return True


class MinutesPerSession(SessionManager):

	minutes = 60
	hours_between_sessions = 23

	def __init__(self, name='DefaultMinutesPerSession', **kwargs):
		super(MinutesPerSession, self).__init__(name, **kwargs)

	def checkSchedule(self):
		return True