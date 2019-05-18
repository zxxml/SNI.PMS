#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from hashlib import sha512
from importlib import import_module

import bcrypt


def hash_pw(pw: str) -> str:
    """hash_pw helps to hash the password for storage.
    This function used salted slow hashing for safety.
    """
    pw_sha512 = sha512(pw.encode('utf-8')).digest()
    pw_bcrypt = bcrypt.hashpw(pw_sha512, bcrypt.gensalt())
    return pw_bcrypt.decode('utf-8')


def check_pw(pw: str, pw_hashed: str) -> bool:
    pw_sha512 = sha512(pw.encode('utf-8')).digest()
    pw_bcrypt = pw_hashed.encode('utf-8')
    return bcrypt.checkpw(pw_sha512, pw_bcrypt)


def import_class(module_name, class_name):
    module = import_module(module_name)
    return getattr(module, class_name)


if __name__ == '__main__':
    print(hash_pw('password'))
