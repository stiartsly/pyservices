import sys
import cherrypy

from lib.logger     import *
from lib.errorCode  import *
from appDeployment  import *
from appAgent       import *
#from appupgrade     import *

def _VS(val):
    # I. ---> Installing
    # E. ---> Enabling
    # E  ---> Enbaled
    # D. ---> Disabling
    # D  ---> Disabled
    # U. ---> Uninstalling
    return val

def _KS(): return "status"
def _KA(): return "applet"
def _KW(): return "webApplet"

class AppSteward():
    logger = None
    appDic = None   # {"thunder": {"status": "Enabled", "applet": object }, ...}

    deployment = None

    def __init__(self, appDeployment):
        self.logger = Logger("AppSteward")
        self.appDic = {}
        self.deployment = appDeployment

    def hasTheApp(self, appName):
        return self.appDic.has_key(appName)

    def installApp(self, appName, appVer):
        self.logger.log("<installApp> Entry.(app:%s,ver:%s)"%(appName, appVer))

        if self.appDic.has_key(appName):
            return EAppAlreadyExisted
        
        ## deploy the zip pkg from server.
        self.appDic[appName] = {_KS(): _VS("I.")}
        retCode = self.deployment.deployApp(appName, appVer)
        if retCode.failed():
            del self.appDic[appName]
            return retCode

        ## try to start as long as finishing deployment
        self.appDic[appName][_KS()] = _VS("E.")
        retCode, applet = AppAgent(appName).callEntry({})
        if retCode.failed():
            del self.appDic[appName]
            return retCode

        self.appDic[appName][_KS()] = _VS("E")
        self.appDic[appName][_KA()] = applet
        return ESuccess

    def uninstallApp(self, appName):
        self.logger.log("<uninstallApp> Entry.(app:%s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoesNotExist

        try:
            status = self.appDic[appName][_KS()]
            retCode = {
                _VS("I.") : lambda: EAppInInstallingProcess  ,
                _VS("E.") : lambda: EAppInEnablingProcess    ,
                _VS("E" ) : lambda: ESuccess                 ,
                _VS("D.") : lambda: EAppInDisablingProcess   ,
                _VS("D" ) : lambda: ESuccess                 ,
                _VS("U.") : lambda: EAppInUninstallingProcess
            }[status]()
            if retCode.failed():
                return retCode
            
            self.appDic[appName][_KS()]= _VS("U.")
            applet = self.appDic[appName][_KA()]
            if status == _VS("E"):
                applet.callExit({}) ## kill app anyway
            
            retCode = self.deployment.undeployApp(appName)
            if retCode.failed():
                self.appDic[appName][_KS()] = _VS("D")
                return retCode

            del self.appDic[appName]
            return ESuccess

        except KeyError:
            self.logger.log("<uninstallApp>{#E}undefined error (app:%s)"%appName)
            return EUndefinedError
            
    def enableApp(self, appName):
        self.logger.log("<enableApp> Entry.(app: %s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoesNotExist

        try:
            status = self.appDic[appName][_KS()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: EAppAlreadyEnabled       ,
                _VS("D."): lambda: EAppInDisablingProcess   ,
                _VS("D" ): lambda: ESuccess                 ,
                _VS("U."): lambda: EAppInUninstallingProcess 
            }[status]()
            if retCode.failed():
                return retCode
            
            self.appDic[appName][_KS()] = _VS("E.")
            retCode, tmp = self.appDic[appName][_KA()].callEntry({})
            if retCode.failed():
                self.appDic[appName][_KS()] = _VS("D")
                return retCode

            self.appDic[appName][_KS()] = _VS("E")
            return ESuccess

        except KeyError:
            self.logger.log("#E<enableApp>{#E} undefined error (app:%s)"%appName)
            return EUndefinedError
        
    def disableApp(self, appName):
        self.logger.log("<disableApp> Entry.(app:%s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoestNotExist

        try:
            status = self.appDic[appName][_KS()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: EAppInDisablingProcess   ,
                _VS("D" ): lambda: EAppAlreadyDisabled      ,
                _VS("U."): lambda: EAppInUninstallingProcess
            }[status]()
            if retCode.failed():
                return retCode

            self.appDic[appName][_KS()] = _VS("D.")
            self.appDic[appName][_KA()].callExit({})  # stop the applet anyway.
            self.appDic[appName][_KS()] = _VS("D")
            return ESuccess
                
        except KeyError:
            self.logger.log("#E<disableApp>{#E} undefined error (app:%s)"%appName)
            return EUndefinedError

    def getAppService(self, appName):
        self.logger.log("<getWebApplet> Entry.(app:%s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoestNotExist

        try: 
            status = self.appDic[appName][_KS()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: EAppInDisablingProcess   ,
                _VS("D" ): lambda: EAppAlreadyDisabled      ,
                _VS("U."): lambda: EAppInUninstallingProcess,
            } [status]()
            if retCode.failed():
                return (retCode, None)

            if self.appDic[appName].has_key(_KW()):
                return (ESuccess, self.appDic[appName][_KW()])
            else:
                return (ESuccess, None)
        except KeyError:
            self.logger.log("#E<getWebApplet>{#E} undefined error (app:%s)"%appName)
            return EUndifinedError

    def mapAppService(self, appName, webApplet):
        self.logger.log("<setWebApplet> Entry.(app:%s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoestNotExist

        try: 
            status = self.appDic[appName][_KS()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: EAppInDisablingProcess   ,
                _VS("D" ): lambda: EAppAlreadyDisabled      ,
                _VS("U."): lambda: EAppInUninstallingProcess,
            } [status]()
            if retCode.failed():
                return retCode

            self.appDic[appName][_KW()] = webApplet
            return ESuccess

        except KeyError:
            self.logger.log("#E<getWebApplet>{#E} undefined error (app:%s)"%appName)
            return EUndifinedError

    def getInstalledAppList(self):
        self.logger.log("<getInstalledAppList> Entry")
        appList = []
        for appName in self.appDic.keys():
            # {"thunder": "enabled", "securecamera": "installing" }
            status = self.appDic[appName][_KS()]
            try:
                val = {
                    _VS("I."): lambda: "Enabled" ,
                    _VS("E."): lambda: "Enabled" ,
                    _VS("E" ): lambda: "Enabled" ,
                    _VS("D."): lambda: "Disabled",
                    _VS("D" ): lambda: "Disabled",
                }[status]()
                appList.append({"appName": appName, "appStatus": val })

            except KeyError:
                pass

        return ESuccessWithMsg(appList)
        
    def fwdMethod(self, method, appName, params):
        self.logger.log("<fwdMethod> Entry(method:%s,app:%s,params:%r)"%(method, appName, params))
        if not self.appDic.has_key(appName):
            return EAppDoesNotExisted

        try: 
            status = self.appDic[appName][_KS()]
            applet = self.appDic[appName][_KA()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: EAppInDisablingPorcess   ,
                _VS("D" ): lambda: EAppAlreadyDisabled      ,
                _VS("U."): lambda: EAppInUninstallingProcess
            } [status]()
            if retCode.failed():
                return retCode

            retCode = {
                "GET" : lambda: applet.callGet(params),
                "POST": lambda: applet.callSet(params)
            } [method]()
            return retCode

        except KeyError:
            return EUndefinedError

    def getAppResource(self, appName, params):
        self.logger.log("<getResource> Entry(app:%s,params:%r)"%(appName, params))
        if not self.appDic.has_key(appName):
            return EAppDoesNotExisted

        try: 
            status = self.appDic[appName][_KS()]
            applet = self.appDic[appName][_KA()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: EAppInEnablingProcess    ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: EAppInDisablingPorcess   ,
                _VS("D" ): lambda: EAppAlreadyDisabled      ,
                _VS("U."): lambda: EAppInUninstallingProcess
            } [status]()
            if retCode.failed():
                return retCode

            return applet.getResource(params)
        except KeyError:
            return EUndefinedError

    def getAppVersion(self, appName):
        self.logger.log("<getAppVersion> Entry(app:%s)"%appName)
        if not self.appDic.has_key(appName):
            return EAppDoesNotExited

        try: 
            status = self.appDic[appName][_KS()]
            applet = self.appDic[appName][_KA()]
            retCode = {
                _VS("I."): lambda: EAppInInstallingProcess  ,
                _VS("E."): lambda: ESuccess                 ,
                _VS("E" ): lambda: ESuccess                 ,
                _VS("D."): lambda: ESuccess                 ,
                _VS("D" ): lambda: ESuccess                 ,
                _VS("U."): lambda: EAppInUninstallingProcess
            } [status]()
            if retCode.failed():
                return retCode

            return ESuccessWithMsg(applet.getVersion())
        except KeyError:
            return EUndefinedError
           
