import sys

from lib.logger       import *
from lib.errorCode    import *
from lib.remoteGetter import *

class _HttpURL():
    host = "10.0.0.15"
    port = "8970"
    reqURL = None

    def __init__(self, reqURL):
        self.reqURL = reqURL

    def toMeta(self):
        return (self.host, self.port, self.reqURL) 

class _SambaURL():
    user = "tangzl"
    pswd = "remote"
    host = "10.0.0.15"
    folder = "/stiartslyT/popostage/staging/upgrade/data"
    filePath = None
    
    def __init__(self, appName, appVersion):
        self.filePath = "/" + appName \
                      + "/" + appVersion \
                      + "/" + appName + ".zip"

    def toMeta(self):
        reqURL = self.folder + self.filePath
        return (self.user, self.pswd, self.host, reqURL)

class _LocalURL():
    filePath = None

    def __init__(self, appName):
        self.filePath = appName + ".zip"

    def toMeta(self):
        return "cache/" + self.filePath

class AppMediator():
    logger = None

    def __init__(self):
        self.logger = Logger("AppMediator")

    def getAvailableAppList(self):
        self.logger.log("<getAvailableAppList> Entry.")
        reqURL = "/availableAppList"
        httpMeta = _HttpURL(reqURL).toMeta()
        retCode, getter = HttpMsgGetter(httpMeta).open()
        if retCode.failed():
            return  EBadRemoteFileURL

        return ESuccessWithMsg(getter.read())
        
    def getAppPackage(self, appName, appVersion):
        self.logger.log("<getAppPkg> Entry(app:%s)"%appName)
        smbMeta = _SambaURL(appName, appVersion).toMeta()
        fileMeta= _LocalURL(appName).toMeta()
        retCode, getter = SambaFileGetter(smbMeta, fileMeta).open()
        if retCode.failed():
            return EBadRemoteFileURL
        
        return getter.readToFile()

        
#-main -----------------------------------------------------------------
if __name__ == "__main__":
    m = AppMediator()
    retCode = m.getAvailableAppList()
    print "retCode:", retCode.dumpMsg() 

    retCode = m.getAppPackage("thunder", "0.0.3")
    print "retCoee:", retCode.dumps()
