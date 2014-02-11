import os
import sys


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