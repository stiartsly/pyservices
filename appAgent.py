import os
import sys
import cherrypy
import importlib
import subprocess

from lib.errorCode import *
from lib.logger    import *

def _readFile(filePath):
    with open(filePath) as file:
        data = file.read()
    return data

PATH_INSTALL = "apps/"

def _toAppInstallWebPath(appName):
    return PATH_INSTALL + appName + "/web"

def _toAppInstallPath(appName):
    return PATH_INSTALL + appName

def _toInstallPath():
    return PATH_INSTALL 

def _toAppModule(appName):
    return appName + ".entry"

def _removeSysPath(path):
    if path in sys.path:
        sys.path.remove(path)

class AppAgent():
    appName = None
    logger  = None
    mod     = None

    def __init__(self, appName):
        self.logger  = Logger("AppAgent:"+appName)
        self.appName = appName
        
    def callEntry(self, params):
        self.logger.log("<callEntry>Entry.(%s)"%self.appName)
        print "installPath: ", _toInstallPath()
        print "installAppPath: ", _toAppInstallPath(self.appName)
        sys.path.append(_toInstallPath())
        sys.path.append(_toAppInstallPath(self.appName))
        try:
            print "---- try import module:", _toAppModule(self.appName)
            self.mod = importlib.import_module(_toAppModule(self.appName))
            #return (ESuccess,self)
        except ImportError:
            self.logger.log("<prepare>{#E} ImportError(mod:%s)."%self.appName)
            return (EAppImportError,None)
            
        print "----> into PopoboxMain"
        self.mod.PopoboxMain(self.appName, params)
        return (ESuccess, self)

    def callExit(self, params):
        self.logger.log("<callExit>Entry(%s,%r)"%(self.appName, params))
        self.mod.PopoboxExit(self.appName, params)

        _removeSysPath(_toAppInstallPath(self.appName))
        _removeSysPath(_toInstallPath())

        if _toAppInstallPath(self.appName) in sys.path:
            print "still have AppInstalPath:", _toAppInstallPath(self.appName)
        if _toInstallPath() in sys.path:
            print "still have InstallPath:", _toInstallPath()

        print "sys.path:", sys.path

        del sys.modules[_toAppModule(self.appName)]
        del sys.modules[self.appName]
        del sys.modules[self.appName + ".sys"]
        del sys.modules[self.appName + ".lib"]

        if _toAppModule(self.appName) in sys.modules.keys():
            print "still have module:", _toAppModule(self.appName)
        if self.appName in sys.modules.keys():
            print "still have module:", self.appName

    def callGet(self, params):
        self.logger.log("<callGet> Entry.(%s,%r)"%(self.appName, params))
        if not params:
            indexPath = _toAppInstallWebPath(self.appName) + "/index.html"
            return ESuccessWithClob(_readFile(indexPath))

        return self.module.PopoboxGetParams(self.appName, params)

    def callSet(self, params):
        self.logger.log("<callSet> Entry.(%s,%r)"%(self.appName, params))
        self.module.PopoboxSetParams(self.appName, params)
        return ESuccess

    def getResource(self, params):
        self.logger.log("<getResource> Entry.(%s,%r)"%(self.appName, params))
        resName = params.replace("_", ".")
        webPath = _toAppInstallWebPath(self.appName)
        for res in os.listdir(webPath):
            if res != resName:
                continue
            return ESuccessWithClob(_readFile(webPath + "/" + resName))
        
        return EBadAppResource

    def getVersion(self):
        self.logger.log("<getVersion> Entry.(%s)"%self.appName)
        verFilePath = _toAppInstallPath(self.appName) + "/version"
        if not os.path.exists(verFilePath):
            return "0.0.1"
        return _readFile(verFilePath)
