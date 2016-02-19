import os
import sys
import cherrypy

from lib.logger     import *
from lib.errorCode  import *
from appSteward     import *
from appDeployment  import *
from appMediator    import *
from appUpgrade     import *

def _matchDefSuffix(resName):
    suffixSet = set(['_html', '_css', '_js'])
    for suffix in suffixSet:
        if resName.endswith(suffix):
            return True
    return False

class WebDummy(object):
    exposed = True
    logger  = None
    message = None

    def __init__(self, msg):
        self.logger = Logger("WebDummy")
        self.message = msg

    def GET(self, **params):
        return ErrorCodeWithMsg(self.message)

    def POSG(self, **params):
        return ErrorCodeWithMsg(self.message)

class AppRootResource(object):
    exposed = True
    logger  = None
    appName = None
    resName = None
    appStwd = None

    def __init__(self, appName, resName, appStwd = None):
        self.logger  = Logger("Resource:" + appName + ":" + resName)
        self.appName = appName
        self.resName = resName 
        self.appStwd = appStwd

    def GET(self, **params):
        self.logger.log("<GET> Entry")
        return self.appStwd.getAppResource(self.appName, self.resName).dumpClob()

    def POST(self, **params): pass

## GET: /appservice/thunder?thunder_active_code=;
## GET: /appservice/sleep?interval
class AppService(object):
    exposed = True
    logger  = None
    appName = None
    appStwd = None
    resDict = None

    def __init__(self, appName, appStwd):
        self.logger  = Logger("AppService:" + appName)
        self.appName = appName
        self.appStwd = appStwd
        self.resDict = {}

    def GET(self, **params):
        self.logger.log("<GET> Entry.(params:%r)"%params)
        retCode = self.appStwd.fwdMethod("GET", self.appName, params)
        return {
            True : lambda retCode: retCode.dumpClob(),
            False: lambda retCode: retCode.dumps()
        } [type(retCode) is ESuccessWithClob](retCode)

    def POST(self, **params):
        self.logger.log("<POST> Entry.(params:%r)"%params)
        return self.appStwd.fwdMethod("POST", self.appName, aprams).dumps()

    def _getRootResource(self, resName):
        if not self.resDict.has_key(resName):
            self.resDict[resName] = AppRootResource(self.appName, resName, self.appStwd)
        return self.resDict[resName]

    def __getattr__(self, name):
        return {
            True : lambda name: self._getRootResource(name),
            False: lambda name: object.__getattr__(name)
        }[_matchDefSuffix(name)](name)

## GET: /appservice/availableAppList
class AvailableAppListService(object):
    exposed  = True
    logger   = None
    mediator = None

    def __init__(self, appMediator):
        self.logger   = Logger("AvailableAppListService")
        self.mediator = appMediator

    def GET(self, **params):
        self.logger.log("[GET]Entry.(params:%r)"%params)
        return self.mediator.getAvailableAppList().dumpMsg()

    def POST(self, **params): pass

## GET: /appservice/installedAppList
class InstalledAppListService(object):
    exposed = True
    logger  = None
    appStwd = None

    def __init__(self, appStwd):
        self.logger  = Logger("InstalledAppListService")
        self.appStwd = appStwd

    def GET(self, **params):
        self.logger.log("[GET]Entry.(params:%r)"%params)
        return self.appStwd.getInstalledAppList().dumps()

    def POST(self, **params): pass
        
########################################################################
### sematic protocols
## POST: /appservice?app=thunder;ver=0.0.1;action=install   --> to install app
## POST: /appservice?app=thunder;action=disable   --> to disable app
## POST: /appservice?app=thunder;action=enable    --> to enable  app
## POST: /appservice?app=thunder;action=uninstall --> to uninstall app
########################################################################
class WebAppService(object):
    exposed = True
    logger  = None
    services  = None

    appStwd    = None
    mediator   = None
    deployment = None
    upgrader   = None


    def __init__(self):
        self.logger     = Logger("WebAppService")
        self.mediator   = AppMediator()
        self.deployment = AppDeployment(self.mediator)
        self.appStwd    = AppSteward(self.deployment)
        self.upgrader   = AppUpgrade(self.appStwd, self.mediator)

        self.services  = {}
        self.services["availableAppList"] = AvailableAppListService(self.mediator)
        self.services["installedAppList"] = InstalledAppListService(self.appStwd) 

        self.upgrader.start()

    def GET(self, **params): 
        pass

    def POST(self, **params):
        self.logger.log("<POST> Entry.(params:%r)"%params)
        appName, action = params["app"], params["action"]
        if params.has_key("ver"):
            appVer = params["ver"]
        retCode = {
            'Install'  : lambda appName: self.appStwd.installApp(appName,appVer),
            'Disable'  : lambda appName: self.appStwd.disableApp(appName),
            'Enable'   : lambda appName: self.appStwd.enableApp(appName),
            'Uninstall': lambda appName: self.appStwd.uninstallApp(appName)
        }[action](appName)
        print "## retCode.dumps():", retCode.dumps()
        return retCode.dumps()

    def DELETE(self, **params):
        pass

    def __getattr__(self, name):
        if self.services.has_key(name):
            return self.services[name]

        if self.appStwd.hasTheApp(name):
            retCode, appService = self.appStwd.getAppService(name)
            if retCode.failed():
                return WebDummy(retCode.dumps())
            if not appService:
                appService = AppService(name, self.appStwd)
                self.appStwd.mapAppService(name, appService)
            return appService 
            
        return object.__getattr__(name)

########################################################################
########################################################################
def _readFile(filePath):
    with open(filePath) as file:
        data = file.read()
    return data

class RootResource(object):
    exposed = True
    logger  = None
    resName = None

    def __init__(self, resName):
        self.logger  = Logger("RootResource:"+resName)
        self.resName = resName

    def GET(self, **params):
        tmpResName= self.resName.replace("_",".")
        for res in os.listdir("web"):
            if res != tmpResName:
                continue
            return _readFile("web/" + tmpResName)
        return None


    def POST(self, **params):
        pass

class RootService(object):
    exposed    = True
    logger     = None
    appservice = None

    def __init__(self):
        self.logger = Logger("RootService")
        self.appservice = WebAppService()

    def GET(self, **params):
        self.logger.log("<GET> Entry(params:%r)"%params)
        if not params:
            return _readFile("web/index.html")
        
    def POST(self, **params):
        pass

    def __getattr__(self, name):
        return {
            True : lambda name: RootResource(name),
            False: lambda name: object.__getattr__(name)
        }[_matchDefSuffix(name)](name)

