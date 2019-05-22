#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime
from enum import IntEnum
from functools import partial, wraps
from hashlib import sha256

import bcrypt
import jsonrpc.exceptions

from sni import db
from sni.db import User


def hash_pw(pw: str) -> str:
    """hash_pw helps to hash the password for storage.
    This function used salted slow hashing for safety.
    """
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = bcrypt.hashpw(pw_sha256, bcrypt.gensalt())
    return pw_bcrypt.decode('utf-8')


def check_pw(pw: str, pw_hashed: str) -> bool:
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = pw_hashed.encode('utf-8')
    return bcrypt.checkpw(pw_sha256, pw_bcrypt)


class DispatchFault(jsonrpc.exceptions.JSONRPCDispatchException):
    """DispatchFault obeys the unspoken rule to have the args member."""
    def __init__(self, code, message, data=None, *args, **kwargs):
        super().__init__(code, message, data, *args, **kwargs)
        self.args = (code, message, data, *args, *kwargs.values())


class Fault(IntEnum):
    GENERAL_400 = 400
    GENERAL_401 = 401
    GENERAL_403 = 403
    GENERAL_418 = 418
    GENERAL_500 = 500
    GENERAL_501 = 501
    GENERAL_508 = 508
    USER_400 = 1400
    USER_409 = 1409
    JOURNAL_400 = 2400
    JOURNAL_409 = 2409
    ARTICLE_400 = 3400
    ARTICLE_409 = 3409
    ARTICLE_412 = 3412

    def __call__(self, message, data=None):
        return DispatchFault(self.value, message, data)

    @property
    def error(self):
        code, message = self.value, self.name
        return DispatchFault(code, message)


def catch_errors(function):
    """Catch GENERAL errors to JSON-RPC errors."""
    @wraps(function)
    def _catch_errors(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except DispatchFault as e:
            # cut the traceback
            raise e from None
        except TypeError as e:
            raise Fault.GENERAL_400(str(e)) from None
        except NotImplementedError as e:
            raise Fault.GENERAL_501(str(e)) from None
        except RecursionError as e:
            raise Fault.GENERAL_508(str(e)) from None
        except Exception as e:
            raise Fault.GENERAL_500(str(e)) from None
    return _catch_errors


def check_session(function):
    """Check whether the session is legal,
    which means it exists and not expired.
    """
    @wraps(function)
    def _check_session(sid, *args, **kwargs):
        try:
            # check whether the session exists
            if not User.exists_db(session=sid):
                message = 'Invalid session token.'
                raise Fault.GENERAL_401(message)
            session = User.get_db(session=sid)
            # check whether the session expired
            if datetime.now() > session.expires:
                message = 'Expired session token.'
                raise Fault.GENERAL_401(message)
        except ValueError:
            message = 'Session ID must be UUID.'
            raise Fault.GENERAL_400(message)
        return function(sid, *args, **kwargs)
    return _check_session


def check_permit(function=None, view_name='Admin'):
    """Check whether the session is legal,
    and the user has the specific permission.
    """
    if function is None:
        # this decorator could be used without brackets
        return partial(check_permit, view_name=view_name)
    # load the class dynamically
    view = getattr(db, view_name)
    @wraps(function)
    @check_session
    def _check_permit(sid, *args, **kwargs):
        if not view.exists_db(session=sid):
            message = 'You must be %s for operation.'
            raise Fault.GENERAL_403(message % view_name)
        return function(sid, *args, **kwargs)
    return _check_permit
