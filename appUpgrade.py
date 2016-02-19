import sys
import time
import threading

from appSteward    import *
from appMediator   import *
from lib.errorCode import *

def _toSplit(version):
    maxV, minV, fixV = version.split(".")
    return (int(maxV), int(minV), int(fixV))

def _needUpgrade(curVer, lastVer):
    curMaxV, curMinV, curFixV = _toSplit(curVer)
    lstMaxV, lstMinV, lstFixV = _toSplit(lastVer)

    return lstMaxV > curMaxV or \
           lstMaxV == curMaxV and lstMinV > curMinV or \
           lstMaxV == curMaxV and lstMinV == curMinV and lstFixV > curFixV 

class AppUpgrade():
    logger   = None
    appStwd  = None
    mediator = None

    def __init__(self, appStwd, appMediator):
        self.logger   = Logger("AppUpgrader")
        self.appStwd  = appStwd
        self.mediator = appMediator
        self.upgdThread = threading.Thread(target=self.upgradeRoutine)

    def start(self):
        self.logger.log("<start> Entry.")
        self.upgdThread.start()
    
    def _getAppUpgdList(self):
        self.logger.log("<_getAppUpgdList> Entry.")
        needUpgd = False
        appUpgdList = []

        retCode = self.mediator.getAvailableAppList()
        if retCode.failed():
            return (needUpgd, None)

        avaiAppList = json.loads(retCode.dumpMsg())["message"]
        for appItem in avaiAppList:
            appName, appVer = appItem["appName"], appItem["appVer"]

            isExisted = self.appStwd.hasTheApp(appName)
            if isExisted:
                print "app(%s) existed"%appName

            if not self.appStwd.hasTheApp(appName):
                continue
            retCode = self.appStwd.getAppVersion(appName)
            if retCode.failed():
                continue

            curVer = retCode.dumpMsg()
            print "app(%s) current version: %s"%(appName, curVer)
            if _needUpgrade(curVer, appVer):
                needUpgd = True
                appUpgdList.append(appItem)
    

        return (needUpgd, appUpgdList)

    def _upgradeApp(self, appName, appVer):
        self.logger.log("<upgradeApp> Entry.(app:%s)"%appName)
        retCode = self.appStwd.uninstallApp(appName)
        if retCode.failed():
            return retCode

        print "------------------------> to install the app (%s)"%appName
        return self.appStwd.installApp(appName, appVer)

    def _upgradeAll(self, appUpgdList):
        self.logger.log("<upgradeAll> Entry.")
        for upgdItem in appUpgdList:
            appName, appVer = upgdItem["appName"], upgdItem["appVer"]
            self._upgradeApp(appName, appVer)
        return ESuccess

    def upgradeRoutine(self):
        self.logger.log("<upgradeRoutine> Entry.")
        while True:
            self.logger.log("<updateRoutine> try to upgrade.")
            needUpgd, appUpgdList = self._getAppUpgdList()
            print "needUpgd: ", needUpgd
            if needUpgd:
                print "upgdList:", appUpgdList
                self._upgradeAll(appUpgdList)
            time.sleep(10)

        
####-----------------------------------------------------------
if __name__ == "__main__":
    mediator = AppMediator()
    upgd = AppUpgrade(None, mediator)
    upgd._checkUpdate()
