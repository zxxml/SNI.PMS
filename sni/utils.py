#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import inspect
import re
from base64 import b64encode
from collections import OrderedDict
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256
from types import MappingProxyType
from uuid import uuid1

import bcrypt
from enforce import runtime_validation as typechecked
from enforce.exceptions import RuntimeTypeError as TypeError
from jsonrpc.exceptions import JSONRPCDispatchException as Fault
from pony.orm.core import ConstraintError, ObjectNotFound, TransactionIntegrityError

from sni import db


def catch_error(function):
    @wraps(function)
    def _catch_error(*args, **kwargs):
        try:
            f = typechecked(function)
            return f(*args, **kwargs)
        except Fault as e:
            # cut the traceback
            raise e from None
        except TypeError:
            text = 'Incorrect type.'
            raise Fault(400, text)
        except ObjectNotFound:
            text = 'Missing object.'
            raise Fault(412, text)
        except ConstraintError:
            text = 'Constraint error.'
            raise Fault(409, text)
        except TransactionIntegrityError:
            text = 'Integrity error.'
            raise Fault(409, text)
        except Exception as e:
            print(type(e), str(e))
            text = 'Server error.'
            raise Fault(500, text)
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
            text = 'Invalid session.'
            raise Fault(401, text)
    # add sessionid parameter to the signature of the wrapped function
    _check_session.__signature__ = signature = inspect.signature(function)
    parameter = ('session', inspect.Parameter('session', inspect.Parameter.POSITIONAL_OR_KEYWORD))
    signature._parameters = MappingProxyType(OrderedDict([parameter, *signature.parameters.items()]))
    return _check_session


def check_user(function):
    @check_session
    @wraps(function)
    def _check_user(session, *args, **kwargs):
        try:
            user = db.Session.get(sessionid=session).user
            assert isinstance(user, db.User)
            return function(*args, **kwargs)
        except AssertionError:
            text = 'User required.'
            raise Fault(403, text)
    return _check_user


def check_admin(function):
    @check_session
    @wraps(function)
    def _check_admin(session, *args, **kwargs):
        try:
            user = db.Session.get(sessionid=session).user
            assert isinstance(user, db.Admin)
            return function(*args, **kwargs)
        except AssertionError:
            text = 'Admin required.'
            raise Fault(403, text)
    return _check_admin


def check_reader(function):
    @check_session
    @wraps(function)
    def _check_reader(session, *args, **kwargs):
        try:
            user = db.Session.get(sessionid=session).user
            assert isinstance(user, db.Reader)
            return function(*args, **kwargs)
        except AssertionError:
            text = 'Reader required.'
            raise Fault(403, text)
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
    regex = re.compile(regex)
    def _check_regex(text):
        result = regex.match(text)
        return result is not None
    return _check_regex


def new_borrowtime(value=None):
    if value is not None:
        return new_returntime(value)
    date = datetime.now().date()
    args = date.timetuple()[:6]
    return datetime(*args)


def new_agreedtime(value=None, default=744):
    if value is not None:
        return new_returntime(value)
    length = timedelta(days=default)
    return new_borrowtime() + length


def new_returntime(value=None):
    """Convert the value to datetime."""
    if value is None: return None
    return datetime.fromtimestamp(value)
