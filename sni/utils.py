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
    general_400 = 400
    general_401 = 401
    general_403 = 403
    general_409 = 409
    general_413 = 413
    general_418 = 418
    general_500 = 500
    general_508 = 508
    # ---------------
    user_400 = 1400
    user_409 = 1409
    user_413 = 1413
    user_418 = 1418
    user_500 = 1500
    user_508 = 1508
    # ---------------
    journal_400 = 2400
    journal_409 = 2409
    journal_413 = 2413
    journal_418 = 2418
    journal_500 = 2500
    journal_508 = 2508
    # ---------------
    article_400 = 3400
    article_409 = 3409
    article_413 = 3413
    article_418 = 3418
    article_500 = 3500
    article_508 = 3508
    # ---------------
    subs_400 = 4400
    subs_409 = 4409
    subs_413 = 4413
    subs_418 = 4418
    subs_500 = 4500
    subs_508 = 4508
    # ---------------
    storage_400 = 5400
    storage_409 = 5409
    storage_413 = 5413
    storage_418 = 5418
    storage_500 = 5500
    storage_508 = 5508
    # ---------------
    borrow_400 = 6400
    borrow_409 = 6409
    borrow_413 = 6413
    borrow_418 = 6418
    borrow_500 = 6500
    borrow_508 = 6508

    def __call__(self, data=None):
        code, message = self.value, self.name
        return JSONRPCDispatchException(code, message, data)

    @property
    def error(self):
        code, message = self.value, self.name
        return JSONRPCDispatchException(code, message)


def catch_errors(function):
    @wraps(function)
    def _catch_errors(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except JSONRPCDispatchException as e:
            # cut the traceback
            raise e from None
        except TypeError as e:
            raise Fault.general_400(str(e))
        except Exception as e:
            raise Fault.general_500(str(e))
    return _catch_errors


def check_session(function):
    @wraps(function)
    def _check_session(sid, *args, **kwargs):
        try:
            if not Session.exists_db(sid=sid):
                raise Fault.general_401.error
            session = Session.get_db(sid=sid)
            if datetime.now() > session.expires:
                raise Fault.general_401.error
        except ValueError as e:
            raise Fault.general_400(str(e))
        return function(sid, *args, **kwargs)
    return _check_session


def check_permit(function=None, view_name='Admin'):
    if function is None:
        return partial(check_permit, view_name=view_name)
    @wraps(function)
    def _check_permit(sid, *args, **kwargs):
        sess = Session.get_db(sid=sid)
        view = getattr(db, view_name)
        if not view.exists_db(uid=sess.uid):
            raise Fault.general_403.error
        return function(sid, *args, **kwargs)
    return _check_permit
