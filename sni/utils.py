#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256
from uuid import uuid1

import bcrypt
from jsonrpc import exceptions
from pony.orm import core

from sni import db


class Fault(exceptions.JSONRPCDispatchException):
    def __init__(self, code, message, details=None):
        super().__init__(code, message.format(details))
        self.args = self.error.code, self.error.message


def catch_error(function):
    @wraps(function)
    def _catch_error(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Fault as e:
            # cut the traceback
            raise e from None
        except (TypeError, ValueError) as e:
            message = 'Invalid arguments: {0}'
            raise Fault(400, message, e.args)
        except core.ConstraintError as e:
            message = 'Constraint error: {0}'
            raise Fault(409, message, e.args)
        except core.TransactionIntegrityError as e:
            message = 'Integrity error: {0}'
            raise Fault(409, message, e.args)
        except core.ObjectNotFound as e:
            message = 'Object not found: {0}'
            raise Fault(412, message, e.args)
        except Exception as e:
            print(type(e), str(e.args))
            message = 'Internal server error: {0}'
            raise Fault(500, message, e.args)
    return _catch_error


def check_session(function):
    @wraps(function)
    def _check_session(sessionid, *args, **kwargs):
        try:
            assert db.Session.exists(sessionid=sessionid)
            session = db.Session.get(sessionid=sessionid)
            assert datetime.now() <= session.shelflife
            return function(sessionid, *args, **kwargs)
        except AssertionError:
            message = 'Invalid session.'
            raise Fault(401, message)
    return _check_session


def check_user(function):
    @check_session
    @wraps(function)
    def _check_user(session, *args, **kwargs):
        try:
            session = db.Session.get(sessionid=session)
            assert db.User.exists(id=session.user.id)
            return function(*args, **kwargs)
        except AssertionError:
            message = 'User required.'
            raise Fault(403, message)
    return _check_user


def check_admin(function):
    @check_session
    @wraps(function)
    def _check_admin(session, *args, **kwargs):
        try:
            session = db.Session.get(sessionid=session)
            assert db.Admin.exists(id=session.user.id)
            return function(*args, **kwargs)
        except AssertionError:
            message = 'Admin required.'
            raise Fault(403, message)
    return _check_admin


def check_reader(function):
    @check_session
    @wraps(function)
    def _check_reader(session, *args, **kwargs):
        try:
            session = db.Session.get(sessionid=session)
            assert db.Reader.exists(id=session.user.id)
            return function(*args, **kwargs)
        except AssertionError:
            message = 'Reader required.'
            raise Fault(403, message)
    return _check_reader


def hash_pw(pw: str) -> str:
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = bcrypt.hashpw(pw_sha256, bcrypt.gensalt())
    return pw_bcrypt.decode('utf-8')


def check_pw(pw: str, pw_hashed: str) -> bool:
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = pw_hashed.encode('utf-8')
    return bcrypt.checkpw(pw_sha256, pw_bcrypt)


def new_shelflife(hours=12):
    """Generate a shelflife with given hours.
    Set the hours to 0 to make it expired."""
    length = timedelta(hours=hours)
    return datetime.now() + length


def new_session(user):
    sessionid = uuid1().hex
    shelflife = new_shelflife()
    return db.Session.new(**locals())


def update_session(user):
    user.session.sessionid = uuid1().hex
    user.session.shelflife = new_shelflife()
    return user.session


def check_regex(regex):
    """Generate a function to match the regex.
    The regex will be compiled to speed up."""
    from re import compile
    regex = compile(regex)
    def _check_regex(text):
        result = regex.match(text)
        return result is not None
    return _check_regex


def new_borrowtime(value=None):
    """Convert the value to datetime.
    Return 0 o'clock today by default."""
    if value is not None:
        return new_returntime(value)
    date = datetime.now().date()
    args = date.timetuple()[:6]
    return datetime(*args)


def new_agreedtime(value=None, default=744):
    if value is not None:
        return new_returntime(value)
    length = timedelta(hours=default)
    return new_borrowtime() + length


def new_returntime(value=None):
    """Convert the value to datetime."""
    if value is None: return None
    return datetime.fromtimestamp(value)
