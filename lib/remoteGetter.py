import os
import sys
import json
import urllib2

from smb.SMBHandler import SMBHandler
from lib.errorCode  import *

BLOCK_SIZE = 4*1024

class RemoteGetter(object):
    fullURL  = None
    
    def __init__(self, fullURL):
        self.fullURL = fullURL

    def open(self): pass
    def read(self): pass

class HttpMsgGetter(RemoteGetter):
    remoteHandler = None

    def __init__(self, httpMeta):
        host, port, reqURL = httpMeta
        httpURL = "http://" + host + ":" + port + reqURL
        super(HttpMsgGetter, self).__init__(httpURL)

    def open(self):
        request = urllib2.Request(self.fullURL)
        request.add_header("Content-Type", "application/json")
        self.remoteHandler = urllib2.urlopen(request)
        return (ESuccess, self)

    def read(self):
        return self.remoteHandler.read()

class HttpFileGetter(RemoteGetter):
    fileName = None
    remoteHandler = None

    def __init__(self, httpMeta, fileName):
        host, port, reqURL = meta
        httpURL = "http://" + hostIP + ":" + port + reqURL
        super(HttpFileGetter, self).__init__(httpURL)
        self.fileName = fileName

    def open(self):
        request = urllib2.request(self.fullURL)
        self.remoteHandler = urllib2.urlopen(request)
        self.localHandler  = open(self.fileName, "w")

        return (ESuccess, self)
        
    def readToFile(self):
        while True:
            data = self.remoteHandler.read(BLOCK_SIZE)
            if data == '':
                break
            self.localHandler.write(data)

        self.localHandler.close()
        return ESuccess

class SambaFileGetter(RemoteGetter):
    fileName = None
    remoteHandler = None
    localHandler  = None
    
    def __init__(self, sambaMeta, fileName):
        user, pswd, hostIP, reqURL = sambaMeta
        smbaURL = "smb://" + user + ":" + pswd + "@" + hostIP + reqURL
        super(SambaFileGetter, self).__init__(smbaURL)
        self.fileName = fileName
        print "fullURL: ", self.fullURL

    def open(self):
        dtor = urllib2.build_opener(SMBHandler)
        self.remoteHandler = dtor.open(self.fullURL)
        self.localHandler  = open(self.fileName, "w")
        
        return (ESuccess, self)  

    def readToFile(self):
        while True:
            data = self.remoteHandler.read(BLOCK_SIZE)
            if data == '':
                break
            self.localHandler.write(data)

        self.localHandler.close()
        return ESuccess

####----------------------------------------------------------------
if __name__ == "__main__":
    ## test 1
    retCode, getter = HttpMsgGetter("10.0.0.15", "8970", "/availableAppList").open()
#    if retCode.succeeded():
    if retCode == 0:
        print getter.read()
    else :
        print "failed to get res"

    ## test2 
    retCode, getter = SambaFileGetter("tangzl", "remote", \
                                    "10.0.0.15", None,\
                                    "/stiartslyT/popostage/staging/upgrade/data/thunder/0.0.3/thunder.zip", "thunder.zip").open()
#    if retCode.succeeded():
    if retCode == 0:
        print "OK"
        getter.readToFile()
    else:
        print "FAILED"
