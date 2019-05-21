#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime
from enum import IntEnum
from functools import partial, wraps
from hashlib import sha256

import bcrypt
from jsonrpc.exceptions import JSONRPCDispatchException

from sni import db
from sni.db import Session


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


class Fault(IntEnum):
    GENERAL_400 = 400
    GENERAL_401 = 401
    GENERAL_403 = 403
    GENERAL_409 = 409
    GENERAL_413 = 413
    GENERAL_418 = 418
    GENERAL_500 = 500
    GENERAL_508 = 508
    # ---------------
    USER_400 = 1400
    USER_409 = 1409
    USER_413 = 1413
    USER_418 = 1418
    USER_500 = 1500
    USER_508 = 1508
    # ---------------
    JOURNAL_400 = 2400
    JOURNAL_409 = 2409
    JOURNAL_413 = 2413
    JOURNAL_418 = 2418
    JOURNAL_500 = 2500
    JOURNAL_508 = 2508
    # ---------------
    ARTICLE_400 = 3400
    ARTICLE_409 = 3409
    ARTICLE_413 = 3413
    ARTICLE_418 = 3418
    ARTICLE_500 = 3500
    ARTICLE_508 = 3508
    # ---------------
    SUBS_400 = 4400
    SUBS_409 = 4409
    SUBS_413 = 4413
    SUBS_418 = 4418
    SUBS_500 = 4500
    SUBS_508 = 4508
    # ---------------
    STORAGE_400 = 5400
    STORAGE_409 = 5409
    STORAGE_413 = 5413
    STORAGE_418 = 5418
    STORAGE_500 = 5500
    STORAGE_508 = 5508
    # ---------------
    BORROW_400 = 6400
    BORROW_409 = 6409
    BORROW_413 = 6413
    BORROW_418 = 6418
    BORROW_500 = 6500
    BORROW_508 = 6508

    def __call__(self, data=None):
        code, message = self.value, self.name
        return JSONRPCDispatchException(code, message, data)

    @property
    def error(self):
        code, message = self.value, self.name
        return JSONRPCDispatchException(code, message)


def catch_errors(function):
    """Catch GENERAL errors to JSON-RPC errors."""
    @wraps(function)
    def _catch_errors(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except JSONRPCDispatchException as e:
            # cut the traceback
            raise e from None
        except TypeError as e:
            raise Fault.GENERAL_400(str(e))
        except RecursionError as e:
            raise Fault.GENERAL_508(str(e))
        except Exception as e:
            raise Fault.GENERAL_500(str(e))
    return _catch_errors


def check_session(function):
    """Check whether the session is legal,
    which means it exists and not expired.
    """
    @wraps(function)
    def _check_session(sid, *args, **kwargs):
        if not Session.exists_db(sid=sid):
            raise Fault.GENERAL_401.error
        session = Session.get_db(sid=sid)
        if datetime.now() > session.expires:
            raise Fault.GENERAL_401.error
        return function(sid, *args, **kwargs)
    return _check_session


def check_permit(function=None, view_name='Admin'):
    """Check whether the session is legal,
    and the user has the specific permission.
    """
    if function is None:
        return partial(check_permit, view_name=view_name)
    @wraps(function)
    @check_session
    def _check_permit(sid, *args, **kwargs):
        sess = Session.get_db(sid=sid)
        view = getattr(db, view_name)
        if not view.exists_db(uid=sess.uid):
            raise Fault.GENERAL_403.error
        return function(sid, *args, **kwargs)
    return _check_permit
