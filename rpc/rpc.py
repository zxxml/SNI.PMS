#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server

from spyne import Application
from spyne.protocol.soap import Soap12
from spyne.server.wsgi import WsgiApplication


class RPCApplication(Application):
    def __init__(self, services, tns, **kwargs):
        kwargs.setdefault('in_protocol', Soap12(validator='lxml'))
        kwargs.setdefault('out_protocol', Soap12())
        super().__init__(services, tns, 'SNI.PMS.RPC', **kwargs)

    def serve_forever(self, host, port, **kwargs):
        wsgi_app = WsgiApplication(self, **kwargs)
        server = make_server(host, port, wsgi_app)
        server.serve_forever(0.5)


if __name__ == '__main__':
    from svcs import UserService

    rpc_app = RPCApplication([UserService], 'SNI.PMS.RPC')
    rpc_app.serve_forever('127.0.0.1', 8080)
