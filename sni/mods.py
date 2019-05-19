#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from functools import partial, wraps

import jsonrpc.exceptions as exc
from pony.orm import TransactionIntegrityError
from typeguard import typechecked

from sni import db
from sni.db import Session


class SniException(exc.JSONRPCDispatchException):
    def __init__(self, code, message=None, *args, **kwargs):
        super().__init__(code, message, *args, **kwargs)
        self.args = (code, message, *args)

    @classmethod
    def bad_request(cls, *args, **kwargs):
        return cls(400, *args, **kwargs)

    @classmethod
    def unauthorized(cls, *args, **kwargs):
        return cls(401, *args, **kwargs)

    @classmethod
    def forbidden(cls, *args, **kwargs):
        return cls(403, *args, **kwargs)

    @classmethod
    def conflict(cls, *args, **kwargs):
        return cls(409, *args, **kwargs)

    @classmethod
    def payload_too_large(cls, *args, **kwargs):
        return cls(413, *args, **kwargs)

    @classmethod
    def teapot(cls, *args, **kwargs):
        """Every status is created equal.
        A teapot can also be well-used.
        """
        return cls(418, *args, **kwargs)

    @classmethod
    def internal(cls, *args, **kwargs):
        return cls(500, *args, **kwargs)

    @classmethod
    def loop_detected(cls, *args, **kwargs):
        return cls(508, *args, **kwargs)


def check_type(function):
    @wraps(function)
    def _check_type(*args, **kwargs):
        try:
            return typechecked(function)(*args, **kwargs)
        except TypeError as e:
            raise SniException.teapot(str(e))
    return _check_type


def check_sess(function):
    @wraps(function)
    def _check_sess(sid, *args, **kwargs):
        if not Session.exists_db(sid=sid):
            raise SniException.unauthorized()
        sess = Session.get_db(sid=sid)
        if datetime.now() > sess.expires:
            raise SniException.unauthorized()
        return function(sid, *args, **kwargs)
    return _check_sess


def check_user(function=None, view_name='Admin'):
    if function is None:
        return partial(check_user, view_name=view_name)
    @wraps(function)
    def _check_user(sid, *args, **kwargs):
        sess = Session.get_db(sid=sid)
        view = getattr(db, view_name)
        if not view.exists_db(uid=sess.uid):
            raise SniException.forbidden()
        return function(sid, *args, **kwargs)
    return _check_user


def wrap_error(function):
    @wraps(function)
    def _wrap_error(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SniException as e:
            raise e from None
        except TransactionIntegrityError as e:
            raise SniException.conflict(str(e))
        except AssertionError as e:
            raise SniException.bad_request(str(e))
        except RecursionError as e:
            raise SniException.loop_detected(str(e))
        except Exception as e:
            raise SniException.internal(str(e))
    return _wrap_error
