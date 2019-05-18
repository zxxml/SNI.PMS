#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import bjoern
from jsonrpc import JSONRPCResponseManager
from werkzeug.wrappers import Request, Response

from sni.db import bind_sqlite
from sni.svcs import d


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(request.data, d)
    return Response(response.json, mimetype='application/json')


def serve_forever(host, port, wsgi_app):
    # bjoern is a fast and lightweight WSGI server
    # using it without any web server is convenient
    socket = bjoern.bind_and_listen(host, port)
    bjoern.server_run(socket, wsgi_app)


def expose_services():
    from configparser import ConfigParser

    config = ConfigParser()
    config.read('./sni.ini')
    host = config['server']['host']
    port = int(config['server']['port'])
    bind_sqlite(config['sqlite']['filename'])
    serve_forever(host, port, application)


if __name__ == '__main__':
    for k, v in d.items():
        print(k, v)
    expose_services()
