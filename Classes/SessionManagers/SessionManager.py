class SessionManager(object):

	ver = Ver('0.0.1')  # Feb 28 2014
    name = ''


    def __init__(self, **kwargs):
    	self.name = kwargs['name']

    def checkSchedule(self):
    	return False
    


class NoTimeOff(SessionManager):

	# no new properties defined here

	def __init__(self, **kwargs):
		super(NoTimeOff,self).__init__(**kwargs)

	def checkSchedule(self):
		return True


class MinutesPerSession(SessionManager):

	minutes = 60
	hoursBetweenSessions = 23
	
	def __init__(self, **kwargs):
		super(NoTimeOff,self).__init__(**kwargs)

	def checkSchedule(self):
		return True