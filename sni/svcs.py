#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import List

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
    user = Admin.new_db(username=username,
                        nickname=nickname,
                        password=password,
                        real_name=real_name,
                        mail_addr=mail_addr,
                        telephone=telephone)
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
    user = Reader.new_db(username=username,
                         nickname=nickname,
                         password=password,
                         real_name=real_name,
                         mail_addr=mail_addr,
                         telephone=telephone)
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


@d.add_method
@return_error
@typechecked
def getJournal(sid: str,
               jid: int,
               name: str,
               issn: str,
               cnc: str,
               pdc: str,
               freq: str,
               addr: str,
               lang: str,
               hist: str,
               used: str):
    pass


@d.add_method
@return_error
@typechecked
def getArticle(sid: str,
               aid: int,
               jid: int,
               title: str,
               author: str,
               content: str,
               keywords: List[str]):
    pass


@d.add_method
@return_error
@typechecked
def getSubs(sid: str,
            jid: int,
            year: int):
    pass


@d.add_method
@return_error
@typechecked
def getStorage(sid: str,
               jid: int,
               year: int,
               vol: int,
               iss: int):
    pass


@d.add_method
@return_error
@typechecked
def getBorrow(sid: str,
              uid: int,
              jid: int,
              borrow_date,
              expect_date,
              return_date):
    pass


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
    print(call_service(uri, 'readerSignUp', ['username', 'nickname', 'password', '', '', '']))
    print(call_service(uri, 'userSignIn', ['username', 'password']))
    print(call_service(uri, 'isAdmin', ['ab181852797d11e9800100000db32364']))
    print(call_service(uri, 'isReader', ['ab181852797d11e9800100000db32364']))
