#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from hashlib import sha512
from typing import Union as U

import bcrypt


def encode_sb(sb: U[str, bytes], encoding: str = 'utf-8'):
    return sb.encode(encoding) if isinstance(sb, str) else sb


def hash_sha512(sb: U[str, bytes]) -> str:
    """hash_sha512 helps to sha512 a str or bytes.
    When str is given, it should be utf-8 encoded.
    """
    sb = encode_sb(sb, 'utf-8')
    return sha512(sb).hexdigest()


def hash_bcrypt(sb: U[str, bytes],
                salt: bytes = None) -> str:
    """hash_bcrypt helps to sha512 a str or bytes.
    If sb is a string, it should be utf-8 encoded.
    Recommend not to specific the salt for safety.
    """
    sb = encode_sb(sb, 'utf-8')
    salt = salt or bcrypt.gensalt()
    result = bcrypt.hashpw(sb, salt)
    return result.decode('utf-8')


def check_bcrypt(sb: U[str, bytes],
                 sb_hashed: U[str, bytes]) -> bool:
    sb = encode_sb(sb, 'utf-8')
    sb_hashed = encode_sb(sb_hashed, 'utf-8')
    return bcrypt.checkpw(sb, sb_hashed)
