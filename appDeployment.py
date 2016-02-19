import os
import sys
import stat
import cherrypy
import urllib2
import zipfile
import shutil

from smb.SMBHandler import SMBHandler
from appMediator    import *
from lib.logger     import *
from lib.errorCode  import *

PATH_CACHE   = "cache/"
PATH_INSTALL = "apps/"

class _FileUnzipper():
    zipFile = None
    srcFile = None
    toPath  = None

    def __init__(self, srcFile, toPath):
        self.srcFile = srcFile
        self.toPath  = toPath
    
    def open(self):
        self.zipFile = zipfile.ZipFile(self.srcFile)

    def unzip(self):
        self.zipFile.extractall(self.toPath)

    def close(self):
        self.zipFile.close()
        os.remove(self.srcFile)

def _getExecPerm():
    return stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO

def _toAppCachePath(appName):
    return PATH_CACHE + appName + ".zip"

def _toAppInstallBinPath(appName):
    return PATH_INSTALL + appName + "/service/bin/"

def _toAppInstallPath(appName):
    return PATH_INSTALL + appName

def _toInstallPath():
    return PATH_INSTALL
    
class AppDeployment():
    logger  = None
    mediator = None

    def __init__(self, appMediator):
        self.logger  = Logger("AppDeployment")   
        self.mediator  = appMediator

    def deployApp(self, appName, appVer):
        self.logger.log("<deploy> Entry.(pkg:%s, ver:%s)"%(appName, appVer))
        retCode = self.mediator.getAppPackage(appName, appVer)
        if retCode.failed():
            return retCode

        appPath = _toAppInstallPath(appName)
        if os.path.exists(appPath):
            shutil.rmtree(appPath)

        srcPath = _toAppCachePath(appName)
        toPath  = _toInstallPath()
        unzipper = _FileUnzipper(srcPath, toPath)
        unzipper.open()
        unzipper.unzip()
        unzipper.close()
         
        appBinPath = _toAppInstallBinPath(appName)
        if not os.path.exists(appBinPath):
            return ESuccess

        for item in os.listdir(appBinPath):
            os.chmod(appBinPath + item, _getExecPerm())
        return ESuccess

    def undeployApp(self, appName):
        self.logger.log("<undeploy> Entry.(pkg:%s)"%appName)
        shutil.rmtree(_toAppInstallPath(appName))
        self.logger.log("<undeploy> Exitry.(app:%s)"%appName)
        return ESuccess

