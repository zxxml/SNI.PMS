#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from pony import orm

from db import Session, User, db
from utils import check_bcrypt, hash_bcrypt, hash_sha512


# @formatter:off
class SignInException(Exception): pass
class SignUpException(Exception): pass
class SignOutException(Exception): pass
# @formatter:on


def sign_in(username, nickname, password):
    if User.exists_db(username=username):
        trace = 'User already exists.'
        raise SignInException(trace)
    sha512_hashed = hash_sha512(password)
    bcrypt_hashed = hash_bcrypt(sha512_hashed)
    user = User.new_db(username, nickname, bcrypt_hashed)
    return Session.new_db(user.uid).sid


@orm.db_session
def sign_up(username, password):
    if not User.exists_db(username=username):
        trace = "User doesn't exist."
        raise SignUpException(trace)
    user = User.get_db(username=username)
    sha512_hashed = hash_sha512(password)
    if not check_bcrypt(sha512_hashed, user.password):
        trace = "Password doesn't match."
        raise SignUpException(trace)
    Session.update_db(user.uid)
    return Session[user.uid].sid


@orm.db_session
def sign_out(sid):
    if not Session.exists_db(sid=sid):
        trace = "Session doesn't exists."
        raise SignOutException(trace)
    session = Session.get_db(sid=sid)
    Session.touch_db(session.uid, 0, 0)


if __name__ == '__main__':
    db.bind('sqlite', ':memory:', create_db=True)
    # db.bind('sqlite', 'sni.db', create_db=True)
    db.generate_mapping(create_tables=True)
