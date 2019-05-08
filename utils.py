#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from hashlib import sha512
from typing import Union as U

import bcrypt


def hash_sha512(sb: U[str, bytes]) -> str:
    """hash_sha512 helps to sha512 a str or bytes.
    When str is given, it should be utf-8 encoded.
    """
    if isinstance(sb, str):
        sb = sb.encode('utf-8')
    return sha512(sb).hexdigest()


def hash_bcrypt(sb: U[str, bytes],
                salt: bytes = None) -> str:
    """hash_bcrypt helps to sha512 a str or bytes.
    If sb is a string, it should be utf-8 encoded.
    Recommend not to specific the salt for safety.
    """
    salt = salt or bcrypt.gensalt()
    if isinstance(sb, str):
        sb = sb.encode('utf-8')
    result = bcrypt.hashpw(sb, salt)
    return result.decode('utf-8')


def check_bcrypt(sb: U[str, bytes],
                 sb_hashed: U[str, bytes]) -> bool:
    if isinstance(sb, str):
        sb = sb.encode('utf-8')
    if isinstance(sb_hashed, str):
        sb_hashed = sb_hashed.encode('utf-8')
    return bcrypt.checkpw(sb, sb_hashed)


if __name__ == '__main__':
    from datetime import datetime

    start_time = datetime.now()
    for i in range(10):
        pw = 'password'.encode('utf-8')
        sha512_hashed = hash_sha512(pw)
        hash_bcrypt(sha512_hashed)
    stop_time = datetime.now()
    print((stop_time - start_time) / 10)
