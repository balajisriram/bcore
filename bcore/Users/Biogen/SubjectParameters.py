from BCore import get_base_path, get_ip_addr, get_mac_address
from BCore.Classes.ClientAndServer.BServer import BServerLocal
from BCore.Classes.Subject import Mouse
from BCore.Classes.Station import StandardVisionHeadfixStation

# User specific protocols
from BCore.Users.Biogen.PhysiologyProtocols import get_phys_protocol_biogen
from BCore.Users.Biogen.BehaviorProtocols import get_behavior_protocol_biogen

import os

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

mac_id = get_mac_address()

def get_protocol_from_name(name):
    if name in ['orientation_tuning_biogen_08292018','short_duration_biogen_08292018']:
        return get_phys_protocol_biogen(name)
    elif name in ['lick_for_reward_biogen_09142018']:
        return get_behavior_protocol_biogen(name)
    else:
        raise ValueError('unknown protocol name')

def load_bserver(path):
    if not os.path.exists(path):
        print("STANDALONERUN:LOAD_BSERVER:Server not found at location. Creating new server by default.")
        b_server = BServerLocal()
        b_server._setup_paths()
        b_server.save()
    else:
        b_server = BServerLocal.load_server(path)  # load the server from path

    return b_server

## MICE currently in use
m_g1_1 = Mouse(subject_id='g1_1', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_2 = Mouse(subject_id='g1_2', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_3 = Mouse(subject_id='g1_3', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_4 = Mouse(subject_id='g1_4', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_5 = Mouse(subject_id='g1_5', gender='Female', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_6 = Mouse(subject_id='g1_6', gender='Female', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_7 = Mouse(subject_id='g1_7', gender='Female', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_8 = Mouse(subject_id='g1_8', gender='Female', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_ctrl_1 = Mouse(subject_id='g1_ctrl_1', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_ctrl_1 = Mouse(subject_id='g1_ctrl_1', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_ctrl_1 = Mouse(subject_id='g1_ctrl_3', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')
m_g1_ctrl_2 = Mouse(subject_id='g1_ctrl_4', gender='Male', birth_date='12/4/2017', strain'C57BL/6', gene_bkgd='WT',reward=10.,timeout=2000.,iacuc_protocol_id='00000823')

## MICE previouly used

## Stations in use


mac_id = get_mac_address()
## get BCore from the default location
b_core = load_bserver(path=BserverLocal.get_standard_server_path())

if mac_id=='':
    b_server.add_subject(m_g1_1)
    b_server.add_subject(m_g1_1)
    b_server.add_subject(m_g1_1)

    # station
    hf_st1 = StandardVisionHeadfixStation(sound_on=True,station_id= 0,station_location=(0,0,0))
    b_server.add_station(hf_st1)

    b_server.change_assignment(m_g1_1,hf_st1.station_id)
    b_server.change_assignment(m_g1_1,hf_st1.station_id)
    b_server.change_assignment(m_g1_1,hf_st1.station_id)

elif mac_id=='':
    b_server.add_subject(m_g1_1)
    b_server.add_subject(m_g1_1)
    b_server.add_subject(m_g1_1)

    # station
    hf_st2 = StandardVisionHeadfixStation(sound_on=True,station_id= 1,station_location=(0,0,1))
    b_server.add_station(hf_st2)

    b_server.change_assignment(m_g1_1,hf_st2.station_id)
    b_server.change_assignment(m_g1_1,hf_st2.station_id)
    b_server.change_assignment(m_g1_1,hf_st2.station_id)
else:
    ValueError('Unknown mac address')
