#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import bjoern
from spyne import Application
from spyne.protocol.soap import Soap12
from spyne.server.wsgi import WsgiApplication

from sni.svcs import UserService


# noinspection PyAbstractClass
class SNIWsgiApplication(WsgiApplication):
    def is_wsdl_request(self, req_env):
        req_env.setdefault('QUERY_STRING', '')
        return super().is_wsdl_request(req_env)


class SNIApplication(Application):
    def __init__(self, services, tns, **kwargs):
        kwargs.setdefault('in_protocol', Soap12(validator='lxml'))
        kwargs.setdefault('out_protocol', Soap12())
        super().__init__(services, tns, 'SNI.PMS.RPC', **kwargs)

    def serve_forever(self, host, port, **kwargs):
        wsgi_app = SNIWsgiApplication(self, **kwargs)
        # bjoern is a fast and lightweight WSGI server
        # using it without any web server is convenient
        socket = bjoern.bind_and_listen(host, port)
        bjoern.server_run(socket, wsgi_app)


if __name__ == '__main__':
    from configparser import ConfigParser

    config = ConfigParser()
    config.read('./sni.ini')
    rpc_app = SNIApplication([UserService], 'SNI.PMS.RPC')
    rpc_app.serve_forever(config['server']['host'],
                          int(config['server']['port']))
