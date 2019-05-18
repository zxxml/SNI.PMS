#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import bjoern
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import WsgiMounter


class SniApplication(Application):
    def __init__(self, services, tns='SNI.PMS', **kwargs):
        kwargs.setdefault('in_protocol', Soap11(validator='lxml'))
        kwargs.setdefault('out_protocol', Soap11())
        super().__init__(services, tns, **kwargs)

    def serve_forever(self, host, port, **kwargs):
        wsgi_app = SniWsgiApplication(self, **kwargs)
        wsgi_app.serve_forever(host, port)


# noinspection PyMethodOverriding
class SniWsgiApplication(WsgiApplication):
    def __init__(self, app, *args, **kwargs):
        if not isinstance(app, Application):
            app = SniApplication(app, app.__name__)
        super().__init__(app, *args, **kwargs)

    def is_wsdl_request(self, req_env):
        req_env.setdefault('QUERY_STRING', '')
        return super().is_wsdl_request(req_env)

    def serve_forever(self, host, port):
        # bjoern is a fast and lightweight WSGI server
        # using it without any web server is convenient
        socket = bjoern.bind_and_listen(host, port)
        bjoern.server_run(socket, self)


class SniWsgiMounter(WsgiMounter):
    def serve_forever(self, host, port):
        # bjoern is a fast and lightweight WSGI server
        # using it without any web server is convenient
        socket = bjoern.bind_and_listen(host, port)
        bjoern.server_run(socket, self)


def expose_services():
    from configparser import ConfigParser
    from sni import svcs

    config = ConfigParser()
    config.read('./sni.ini')
    host = config['server']['host']
    port = int(config['server']['port'])
    wsgi_mounter = SniWsgiMounter({
        'user': SniApplication([svcs.UserService]),
        'subs': SniApplication([svcs.SubsService]),
        'storage': SniApplication([svcs.StorageService]),
        'article': SniApplication([svcs.ArticleService]),
        'search': SniApplication([svcs.SearchService]),
        'borrow': SniApplication([svcs.BorrowService]),
    })
    wsgi_mounter.serve_forever(host, port)


if __name__ == '__main__':
    expose_services()
