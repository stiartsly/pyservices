import sys
import json

errorDic = {
    0   : "ESuccess"                ,
    2001: "EAppAlreadyExisted"      ,
    2002: "EAppDoesNotExist"        ,
    2003: "EAppInInstallingProcess" ,
    2004: "EAppInDisabingProcess"   ,
    2005: "EAppInEnablingProcess"   ,
    2006: "EAppInUninstallingProcess",
    2007: "EAppAlreadyEnabled"      ,
    2008: "EAppAlreadyDisabled"     ,
    2009: "EAppPkgDoesNotExist"     ,
    2010: "EAppDownloadFailed"      ,
    2011: "EBadRemoteFileURL"       ,
    2012: "EAppImportError"         ,
    2013: "EBadAppResource"         ,
    2014: "EBadRootResource"        ,
    
    2100: "EUndefinedError"     
}

class ErrorCode(object):
    errCode = None

    def __init__(self, errCode):
        self.errCode = errCode
    
    def _toDict(self):
        return {"result" : errorDic[self.errCode] }

    def failed(self):
        return self.errCode != 0

    def succeeded(self):
        return self.errCode == 0

    def dumps(self):
        return json.dumps(self._toDict())

ESuccess                  = ErrorCode(0)
EAppAlreadyExisted        = ErrorCode(2001)
EAppDoesNotExist          = ErrorCode(2002)
EAppInInstallingProcess   = ErrorCode(2003)
EAppInEnablingProcess     = ErrorCode(2004)
EAppInDisablingProcess    = ErrorCode(2005)
EAppInUninstallingProcess = ErrorCode(2006)
EAppAlreadyEnabled        = ErrorCode(2007)
EAppAlreadyDisabled       = ErrorCode(2008)
EAppPkgDoesNotExist       = ErrorCode(2009)
EAppDownloadFailed        = ErrorCode(2010)
EBadRemoteFileURL         = ErrorCode(2011)
EAppImportError           = ErrorCode(2012)
EBadAppResource           = ErrorCode(2013)
EBadRootResource          = ErrorCode(2014)

EUndefinedError           = ErrorCode(2100)

class ErrorCodeWithMsg(ErrorCode):
    message = None

    def __init__(self, errCode, message):
        super(ErrorCodeWithMsg, self).__init__(errCode)
        self.message = message

    def _toDict(self):
        return {"result" : errorDic[self.errCode],
                "message": self.message }

    def dumps(self):
        return json.dumps(self._toDict())

class ESuccessWithMsg(ErrorCodeWithMsg):
    def __init__(self, message):
        super(ESuccessWithMsg, self).__init__(0, message)

    def dumpMsg(self):
        return self.message

class ESuccessWithClob(ErrorCodeWithMsg):
    def __init__(self, clobData):
        super(ESuccessWithClob, self).__init__(0, clobData)
    
    def dumpClob(self):
        return self.message

###--------------------------------------------------------------
if __name__ == "__main__":
    tiger = ErrorCodeWithMsg(2005, {"animal":"tiger"})
    tiger.dumps()

    cat = ESuccessWithMsg({"flower":"rose"})
    cat.dumps()
   
