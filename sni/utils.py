#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from functools import wraps
from hashlib import sha512

import bcrypt
from jsonrpc.exceptions import JSONRPCDispatchException
from jsonrpc.exceptions import JSONRPCInternalError





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


