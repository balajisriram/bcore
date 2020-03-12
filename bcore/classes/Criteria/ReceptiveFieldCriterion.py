import bcore.Classes.Criterion as crit

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

class ReceptiveFieldCriterion(crit.Criterion):

    def __init__(self, **kwargs):
        super(ReceptiveFieldCriterion, self).__init__(**kwargs)

    def graduate(self, **kwargs):
        return False