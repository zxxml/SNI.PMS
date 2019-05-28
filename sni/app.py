#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser

import bjoern
import ujson
from jsonrpc import JSONRPCResponseManager
from jsonrpc.utils import JSONSerializable
from werkzeug.wrappers import Request, Response

from sni.db import bind_sqlite
from sni.rpc import d


@Request.application
def application(request):
    print(request.data)
    response = JSONRPCResponseManager.handle(request.data, d)
    response._data['result'] = '中文测试'
    print(response.json)
    return Response(response.json, mimetype='application/json')


def serve_forever(host, port):
    JSONSerializable.serialize = ujson.dumps
    JSONSerializable.deserialize = ujson.loads
    # bjoern is a fast and lightweight WSGI server
    # using it without any web server is convenient
    socket = bjoern.bind_and_listen(host, port)
    bjoern.server_run(socket, application)


def start_application():
    cfg = ConfigParser()
    cfg.read('sni.ini')
    host = cfg['server']['host']
    port = cfg['server']['port']
    bind_sqlite(cfg['sqlite']['path'])
    serve_forever(host, int(port))


if __name__ == '__main__':
    print(d.keys())
    start_application()
