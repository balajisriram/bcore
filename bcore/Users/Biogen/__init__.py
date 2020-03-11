__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

from .BehaviorProtocols import get_behavior_protocol_biogen
from .PhysiologyProtocols import get_phys_protocol_biogen

def get_protocol_from_name(name):
    if name in ['orientation_tuning_biogen_08292018','ortune','short_duration_biogen_08292018','orsdp']:
        return get_phys_protocol_biogen(name)
    elif name in ['lick_for_reward_biogen_09142018','lfr',
                  'classical_conditioning_protocol_12022018','ccp',
                  'auditory_go_protocol_12192018','audgo',
                  'gratings_go_protocol_12202018','gratgo']:
        return get_behavior_protocol_biogen(name)
    else:
        raise ValueError('unknown protocol name')
