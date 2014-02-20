import os
import sys
import socket
import time


def getBaseDirectory():
    base = os.path.split(os.path.abspath(__file__))
    base = os.path.split(base[0])
    return base[0]


def addPaths():
    # make a list of all the directories in the os.walk of the base
    # directory and then remove the .git or .svn components
    baseDirTree = [
                  dirs[0] for dirs in
                  os.walk(os.path.join(getBaseDirectory(), 'b-core'))
                  if ('.git' or '.svn') not in dirs[0]
                  ]
                  # make a list of all the directories
    sys.path.append(baseDirTree)
    print('INFO:: added module fodlers to path')


def getIPAddr():
    return ([
        ip for ip in socket.gethostbyname_ex(
            socket.gethostname()
            )[2] if not ip.startswith("127.")][:1])


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