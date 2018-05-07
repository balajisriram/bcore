import os
import sys
import time
import struct

__author__ = "Balaji Sriram"
__version__ = "0.0.1"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Balaji Sriram"
__email__ = "balajisriram@gmail.com"
__status__ = "Production"

def get_base_directory():
    base = os.path.split(os.path.abspath(__file__))
    base = os.path.split(base[0])
    return base[0]


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
    import platform
    
    if platform.system()=='Linux':
        import socket
        if not args:
            ifname = 'lo0'
        else:
            ifname = args[0]

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8927,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
                )[20:24])
        except IOError:
            ip = ''
    elif platform.system()=='Windows':
        import socket
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip = s.getsockname()[0]
    return ip


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
