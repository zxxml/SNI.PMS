#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Union

from jsonrpc import Dispatcher
from pony import orm
from typeguard import typechecked

from sni.db import Admin, Reader, Session, User
from sni.mods import Status, return_error
from sni.utils import check_pw, hash_pw

__all__ = ['d']
d = Dispatcher()


@orm.db_session
def check_session(sid: str):
    if not Session.exists_db(sid=sid):
        raise Status.session_400.error
    sess = Session.get_db(sid=sid)
    if datetime.now() < sess.expires:
        raise Status.session_401.error
    return sess


@d.add_method
@return_error
@typechecked
def adminSignUp(username: str,
                nickname: str,
                password: str,
                real_name: Union[str, None],
                mail_addr: Union[str, None],
                telephone: Union[str, None]):
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
                 real_name: Union[str, None],
                 mail_addr: Union[str, None],
                 telephone: Union[str, None]):
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
@orm.db_session
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
@orm.db_session
def userSignOut(sid: str):
    sess = check_session(sid)
    Session.touch_db(sess.uid, 0, 0)


@d.add_method
@return_error
@typechecked
@orm.db_session
def isAdmin(sid: str):
    sess = check_session(sid)
    return Admin.exists_db(uid=sess.uid)


@d.add_method
@return_error
@typechecked
@orm.db_session
def isReader(sid: str):
    sess = check_session(sid)
    return Reader.exists_db(uid=sess.uid)


@d.add_method
@return_error
@typechecked
@orm.db_session
def getJournal(sid: str,
               jid: Union[int, None],
               name: Union[str, None],
               issn: Union[str, None],
               cnc: Union[str, None],
               pdc: Union[str, None],
               freq: Union[str, None],
               addr: Union[str, None],
               lang: Union[str, None],
               hist: Union[str, None],
               used: Union[str, None]):
    pass


@d.add_method
@return_error
@typechecked
@orm.db_session
def getArticle(sid: str,
               aid: Union[int, None],
               jid: Union[int, None],
               title: Union[str, None],
               author: Union[str, None],
               content: Union[str, None],
               keywords: List[str]):
    pass


@d.add_method
@return_error
@typechecked
@orm.db_session
def getSubs(sid: str,
            jid: Union[int, None],
            year: Union[int, None]):
    pass


@d.add_method
@return_error
@typechecked
@orm.db_session
def getStorage(sid: str,
               jid: Union[int, None],
               year: Union[int, None],
               vol: Union[int, None],
               iss: Union[int, None]):
    pass


@d.add_method
@return_error
@typechecked
@orm.db_session
def getBorrow(sid: str,
              uid: Union[int, None],
              jid: Union[int, None],
              borrow_date: Union[str, None],
              expect_date: Union[str, None],
              return_date: Union[str, None]):
    pass
