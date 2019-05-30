#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime
from json import JSONEncoder

import bjoern
import simplejson
from jsonrpc import JSONRPCResponseManager
from jsonrpc.utils import JSONSerializable
from werkzeug.wrappers import Request, Response

from sni import db, rpc


class DatetimeEncoder(JSONEncoder):
    """Help to jsonify the datetime.
    Still need to loads it manually."""
    def default(self, o):
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(0)

    @classmethod
    def dumps(cls, o):
        """dumps method supports datetime."""
        return simplejson.dumps(o, cls=cls)

    @classmethod
    def loads(cls, s):
        """loads method supports datetime."""
        return simplejson.loads(s)


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(request.data, rpc.d)
    return Response(response.json, mimetype='application/json')


def serve_forever(host, port):
    JSONSerializable.serialize = DatetimeEncoder.dumps
    JSONSerializable.deserialize = DatetimeEncoder.loads
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
