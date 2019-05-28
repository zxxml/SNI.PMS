#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from configparser import ConfigParser
from datetime import datetime, timedelta
from hashlib import sha256

import bcrypt

from sni.db import Admin, Reader, User

cfg = ConfigParser()
cfg.read('sni.ini')


def new_expire(days=None, hours=None):
    days = days or int(cfg['session']['days'])
    hours = hours or int(cfg['session']['hours'])
    length = timedelta(days=days, hours=hours)
    return datetime.now() + length


def hash_pw(pw: str) -> str:
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = bcrypt.hashpw(pw_sha256, bcrypt.gensalt())
    return pw_bcrypt.decode('utf-8')


def check_pw(pw: str, pw_hashed: str) -> bool:
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    pw_bcrypt = pw_hashed.encode('utf-8')
    return bcrypt.checkpw(pw_sha256, pw_bcrypt)


def check_user(sess_id):
    user = User.get(sess_id=sess_id)
    return user and datetime.now() < user.expires


def check_admin(sess_id):
    user = Admin.get(sess_id=sess_id)
    return user and datetime.now() < user.expires


def check_reader(sess_id):
    user = Reader.get(sess_id=sess_id)
    return user and datetime.now() < user.expires


def clean_locals(locals_, *keys):
    return {k: locals_[k] for k in locals_
            if k != 'sessId' and k not in keys}
