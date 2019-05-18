#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from jsonrpc import Dispatcher
from typeguard import typechecked

from sni.db import Admin, Reader, Session, User
from sni.mods import Status, return_error
from sni.utils import check_pw, hash_pw

__all__ = ['d']
d = Dispatcher()


@d.add_method
@return_error
@typechecked
def adminSignUp(username: str,
                nickname: str,
                password: str,
                real_name: str,
                mail_addr: str,
                telephone: str):
    if User.exists_db(username=username):
        raise Status.username_409.error
    password = hash_pw(password)
    user = Admin.new_db(username,
                        nickname,
                        password,
                        real_name,
                        mail_addr,
                        telephone)
    sess = Session.new_db(user.uid)
    return sess.sid.hex


@d.add_method
@return_error
@typechecked
def readerSignUp(username: str,
                 nickname: str,
                 password: str,
                 real_name: str,
                 mail_addr: str,
                 telephone: str):
    if User.exists_db(username=username):
        raise Status.username_409.error
    password = hash_pw(password)
    user = Reader.new_db(username,
                         nickname,
                         password,
                         real_name,
                         mail_addr,
                         telephone)
    sess = Session.new_db(user.uid)
    return sess.sid.hex


@d.add_method
@return_error
@typechecked
def userSignIn(username: str, password: str):
    if not User.exists_db(username=username):
        raise Status.username_400.error
    user = User.get_db(username=username)
    if not check_pw(password, user.password):
        raise Status.password_400.error
    Session.update_db(user.uid)
    sess = Session.get_db(uid=user.uid)
    return sess.sid.hex


@d.add_method
@return_error
@typechecked
def userSignOut(sid: str):
    if not Session.exists_db(sid=sid):
        raise Status.session_400.error
    sess = Session.get_db(sid=sid)
    Session.touch_db(sess.sid, 0, 0)


@d.add_method
@return_error
@typechecked
def isAdmin(sid: str):
    if not Session.exists_db(sid=sid):
        raise Status.session_400.error
    sess = Session.get_db(sid=sid)
    return Admin.exists_db(uid=sess.uid)


@d.add_method
@return_error
@typechecked
def isReader(sid: str):
    if not Session.exists_db(sid=sid):
        raise Status.session_400.error
    sess = Session.get_db(sid=sid)
    return Reader.exists_db(uid=sess.uid)


def call_service(url, method, params, **kwargs):
    """Example codes to call web service."""
    import requests
    headers = {'content-type': 'application/json'}
    payload = {
        'method': method,
        'params': params,
        'jsonrpc': '2.0',
        'id': 0
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json(**kwargs)


if __name__ == '__main__':
    uri = 'http://linkfire.cn:8080/jsonrpc'
    print(call_service(uri, 'isAdmin', ['123456']))
