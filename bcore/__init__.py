import os
import sys
import time
import struct
import uuid
import re
import platform
import netifaces as ni
import json

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

DATETIME_TO_STR = '%B-%m-%Y::%H:%M:%S'


def get_codebase_path():
    # returns the directory under the BCore directory
    base = os.path.split(os.path.abspath(__file__))
    base = os.path.split(base[0])
    base = os.path.split(base[0])
    return(base[0])

def get_config_path():
    base = get_base_path()
    config_path = os.path.join(base,'.bcore')
    return config_path

def get_base_path():
    temp = json.load(os.path.join(get_config_path(),'bcore.config'))
    return temp['base_path']

def add_paths():
    # make a list of all the directories in the os.walk of the base
    # directory and then remove the .git or .svn components
    base_dir_tree = [
                  dirs[0] for dirs in
                  os.walk(os.path.join(getBaseDirectory(), 'BCore'))
                  if ('.git' or '.svn') not in dirs[0]
                  ]
                  # make a list of all the directories
    sys.path.append(baseDirTree)
    print('INFO:: added module folders to path')
    

def get_ip_addr(*args):
    """
        Code from : http://code.activestate.com/recipes/439094/
    """
    if platform.system()=='Linux':
        if 'enp4s0' in ni.interfaces():
            return ni.ifaddresses('enp4s0')[ni.AF_INET][0]['addr']
        elif 'eth0' in ni.interfaces():
            return ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    elif platform.system()=='Windows':
        import socket
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        return s.getsockname()[0]


def get_time_stamp(*arg):
    if len(arg) > 1:
        raise ValueError('only a single timestamp in a single run')
    elif len(arg) == 0:
        t = time.time()
    else:
        t = arg[0]

    try:
        localtime = time.localtime(t)
    except TypeError:  # check if a localtime 9-item seq was sent
        try:
            # use mktime to convert if possible
            t = time.mktime(t)
            localtime = time.localtime(t)
        except Exception:
            raise Exception
    else:
        milliseconds = '%03d' % int((t - int(t)) * 1000)
        return time.strftime('D%m%d%YT%H%M%SM', localtime) + milliseconds

def get_mac_address():
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac
