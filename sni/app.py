#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import json
from configparser import ConfigParser
from datetime import datetime

import bjoern
from jsonrpc import JSONRPCResponseManager
from jsonrpc.utils import JSONSerializable
from werkzeug.wrappers import Request, Response

from sni import db, rpc


class JsonEncoder(json.JSONEncoder):
    """Help to jsonify the datetime.
    Still need to loads it manually."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(0)

    @classmethod
    def dumps(cls, o):
        return json.dumps(o, cls=cls)

    @classmethod
    def loads(cls, s):
        return json.loads(s)


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(request.data, rpc.d)
    return Response(response.json, mimetype='application/json')


def serve_forever(host, port):
    rpc.guest_sign_up('Guest', 'Guest', 'Guest')
    JSONSerializable.serialize = JsonEncoder.dumps
    JSONSerializable.deserialize = JsonEncoder.loads
    # bjoern is a fast and lightweight WSGI server
    # using it without any web server is convenient
    socket = bjoern.bind_and_listen(host, port)
    bjoern.server_run(socket, application)


def start_application():
    cfg = ConfigParser()
    cfg.read('sni.ini')
    host = cfg['server']['host']
    port = cfg['server']['port']
    db.bind_sqlite(cfg['sqlite']['path'])
    serve_forever(host, int(port))


if __name__ == '__main__':
    print(rpc.d.keys())
    start_application()
