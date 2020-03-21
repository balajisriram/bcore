"""
CHANGEPARAMS looks for a change_params.pkl structured as follows:
    change_params = {'changes_for':'Aug-21-2018',
                     'changes':[change1,change2,change3,...]}
    change1 = ['add_subject',subject_params]
    change2 = ['remove_subject',subject_id]
    change3 = ['change_reward',(subject_id,val)]
    change4 = ['change_timeout',(subject_id,val)]
    change4 = ['change_timeout',(subject_id,val)]
    change4 = ['change_timeout',(subject_id,val)]
"""
import sys
import os
import pickle
import datetime
from dateutil.parser import parse
from BCore import get_mac_address, get_base_path
from BCore.Classes.ClientAndServer.BServer import BServerLocal
from BCore.Classes.Protocol import DemoGratingsProtocol
from BCore.Classes.Subject import get_subject
from BCore.Classes.Station import StandardVisionBehaviorStation,StandardKeyboardStation

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

def load_standard_bserver():
    bserver_path = BServerLocal.get_standard_server_path()
    b_server = BServerLocal.load_server(bserver_path)
    return b_server

def load_change_params():
    path = os.path.join(get_base_path(),'BCoreData','ChangeParams','change_params.pkl')
    if os.path.exist(path):
        with open(path,'rb') as f:
            change_params = pickle.load(f)
        curr_time = datetime.datetime.now().strftime('m%md%dy%YT%H%M')
        path_new = os.path.join(get_base_path(),'BCoreData','ChangeParams','change_params.'+curr_time)
        os.rename(path,path_new)
    else:
        change_params = None
    return change_params

if __name__=="__main__":
    b_server = load_standard_bserver()
    params = load_change_params()
    if not params:
        return 0
    # verify that the changes requested are current
    curr_time = datetime.datetime.now()
    changes_for = parse(params['changes_for'])
    t_delta = abs(curr_time-changes_for)
    go = 'y'
    if t_delta>datetime.timedelta(1)
        print('Requesting changes for '+params['changes_for'])
        go = input('Continue? (y/n):')
        if go=='n':return 0
    for change in params['changes']:
        if change[0]=='add_subject':
            subj = get_subject(change[1])
            b_server.add_subject(subj)
            print('ChangeParams::Added Subject with id {0}'.format(subj.subject_id))
        elif change[0]=='remove_subject':
            assert change[1] in b_server.get_subject_ids(), 'Cannot remove subject not in the server'
            b_server.remove_subject(change[1])
            print('ChangeParams::Removed Subject with id {0}'.format(change[1]))
        elif change[0]=='change_reward':
            assert change[1][0] in b_server.get_subject_ids(), 'Cannot change reward for subject not in the server'
            b_server.change_reward(change[1][0],change[1][1])
            print('ChangeParams::Changed reward for {0}'.format(change[1][0]))
        elif change[0]=='change_timeout':
            assert change[1][0] in b_server.get_subject_ids(), 'Cannot change timeout for subject not in the server'
            b_server.change_timeout(change[1][0],change[1][1])
            print('ChangeParams::Changed timeout for {0}'.format(change[1][0]))
