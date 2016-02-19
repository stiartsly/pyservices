import os
import sys
import subprocess

from lib.errorCode import *

nativeProgs = ["python"]

def CreateProcess(appName, binPath, args):
    #todo:
    if binPath in nativeProgs:
        binRunPath = binPath
    elif binPath[0] == "/":
        binRunPath = binPath
    else:
        binRunPath = "apps/" + appName + "/service/" + binPath

    print "<CreateProcess> binRunPath: ", binRunPath
    child = subprocess.Popen([binRunPath, args])
    print "<CreateProcess> child: ", child
    return (ESuccess, child)

def KillProcess(process):
    print "<KillProcess> to kill a process"
    ret = process.poll()
    print "<KillProcess ret: ", ret
    if ret == None:
        process.kill()
    process.wait()


def PollProcess(process):
    return process.poll


def WaitProcess(process):
    return process.wait()
    
