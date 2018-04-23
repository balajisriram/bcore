from verlib import NormalizedVersion as Ver

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class SessionManager(object):

	ver = Ver('0.0.1')  # Feb 28 2014
	name = ''


	def __init__(self, name='Unknown', **kwargs):
		self.name = name

	def check_schedule(self):
		return False
    


class NoTimeOff(SessionManager):

	# no new properties defined here

	def __init__(self, name='DefaultNoTimeOff', **kwargs):
		super(NoTimeOff,self).__init__(name, **kwargs)

	def check_schedule(self):
		return True


class MinutesPerSession(SessionManager):

	minutes = 60
	hours_between_sessions = 23

	def __init__(self, name='DefaultMinutesPerSession', **kwargs):
		super(MinutesPerSession, self).__init__(name, **kwargs)

	def check_schedule(self):
		return True