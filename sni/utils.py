#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime, timedelta
from functools import wraps
from hashlib import sha256
from uuid import uuid1

import bcrypt

from sni import db


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


def check_session(function):
    @wraps(function)
    def _check_session(sessionid, *args, **kwargs):
        assert db.Session.exists(sessionid=sessionid)
        session = db.Session.get(sessionid=sessionid)
        assert datetime.now() <= session.shelflife
        return function(sessionid, *args, **kwargs)
    return _check_session


def check_user(function):
    @check_session
    @wraps(function)
    def _check_user(sessionid, *args, **kwargs):
        user = db.Session.get(sessionid=sessionid).user
        assert isinstance(user, db.User)
        return function(*args, **kwargs)
    return _check_user


def check_admin(function):
    @check_session
    @wraps(function)
    def _check_admin(sessionid, *args, **kwargs):
        user = db.Session.get(sessionid=sessionid).user
        assert isinstance(user, db.Admin)
        return function(*args, **kwargs)
    return _check_admin


def check_reader(function):
    @check_session
    @wraps(function)
    def _check_reader(sessionid, *args, **kwargs):
        user = db.Session.get(sessionid=sessionid).user
        assert isinstance(user, db.Reader)
        return function(*args, **kwargs)
    return _check_reader
