#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from base64 import b64encode
from hashlib import sha256

import bcrypt
from pony.orm.serialization import to_dict


def hash_pw(pw):
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    return bcrypt.hashpw(pw_sha256, bcrypt.gensalt()).decode('utf-8')


def check_pw(pw, pw_hashed):
    pw_sha256 = b64encode(sha256(pw.encode('utf-8')).digest())
    return bcrypt.checkpw(pw_sha256, pw_hashed.encode('utf-8'))


def unpack_model(complex_model, *ignored_attrs):
    attributes = complex_model.as_dict()
    return {k: v for k, v in attributes.items()
            if k not in ignored_attrs}


def pack_entity(entity, *ignored_attrs):
    attributes = to_dict(entity)
    return {k: v for k, v in attributes.items()
            if k not in ignored_attrs}
