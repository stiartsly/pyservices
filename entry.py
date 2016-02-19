import sys
import cherrypy

from webServices import * 

root = RootService()

conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 1970,
        'tools.encode.on':True, 
        'tools.encode.encoding':'utf8', 
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}

cherrypy.quickstart(root, '/', conf)
