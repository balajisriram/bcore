import os
import sys
import socket
import time
import fcntl
import struct

# import git


def getBaseDirectory():
    base = os.path.split(os.path.abspath(__file__))
    base = os.path.split(base[0])
    return base[0]


def addPaths():
    # make a list of all the directories in the os.walk of the base
    # directory and then remove the .git or .svn components
    baseDirTree = [
                  dirs[0] for dirs in
                  os.walk(os.path.join(getBaseDirectory(), 'BCore'))
                  if ('.git' or '.svn') not in dirs[0]
                  ]
                  # make a list of all the directories
    sys.path.append(baseDirTree)
    print('INFO:: added module fodlers to path')


def getIPAddr(*args):
    """
        Code from : http://code.activestate.com/recipes/439094/
    """
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
    return ip


def getTimeStamp(*arg):
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


# def gitpull(**kwargs):
#     """
#         Use function only if you know what you are doing. Pulling changes while
#         the function is running will randomly cause the earth to flip magnetic
#         poles
# 
#         But seriously, in cases where there has not been any git checkouts of
#         a different branch. For simple git pulls, if the pyc timestamp is
#         different, python will do the right thing
#     """
#     if kwargs:
#         gitdir = kwargs['gitdir']
#     else:
#         gitdir = os.path.join(getBaseDirectory(), 'BCore')
#     g = git.cmd.Git(gitdir)
#     g.pull()