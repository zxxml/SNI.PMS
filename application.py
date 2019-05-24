#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import bjoern
import spyne
from spyne.protocol.json import JsonDocument
from spyne.server import wsgi

from tables import bind_sqlite
from services import UserService


class Application(spyne.Application):
    def __init__(self, services, tns='SNI.PMS', name='SNI.PMS', **kwargs):
        kwargs.setdefault('in_protocol', JsonDocument(validator='soft'))
        kwargs.setdefault('out_protocol', JsonDocument(validator='soft'))
        super().__init__(services, tns, name, **kwargs)


# noinspection PyMethodOverriding
class WsgiApplication(wsgi.WsgiApplication):
    def is_wsdl_request(self, req_env):
        req_env.setdefault('QUERY_STRING', '')
        return super().is_wsdl_request(req_env)

    def serve_forever(self, host, port):
        socket = bjoern.bind_and_listen(host, port)
        bjoern.server_run(socket, self)


def start_application():
    application = Application([UserService])
    wsgi_application = WsgiApplication(application)
    wsgi_application.serve_forever('0.0.0.0', 8080)


if __name__ == '__main__':
    bind_sqlite(':memory:')
    start_application()
