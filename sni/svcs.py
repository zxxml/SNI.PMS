#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import Optional

from jsonrpc import Dispatcher
from pony import orm

from sni.db import Admin, Journal, Reader, Session, User
from sni.mods import check_sess, check_type, check_user, wrap_error
from sni.utils import check_pw, hash_pw

__all__ = ['d']
d = Dispatcher()


@d.add_method
@wrap_error
@check_type
def adminSignUp(username: str,
                nickname: str,
                password: str,
                real_name: Optional[str],
                mail_addr: Optional[str],
                telephone: Optional[str]):
    password = hash_pw(password)
    user = Admin.new_db(**locals())
    sess = Session.new_db(user.uid)
    return sess.sid.hex


@d.add_method
@wrap_error
@check_type
def readerSignUp(username: str,
                 nickname: str,
                 password: str,
                 real_name: Optional[str],
                 mail_addr: Optional[str],
                 telephone: Optional[str]):
    password = hash_pw(password)
    user = Reader.new_db(**locals())
    sess = Session.new_db(user.uid)
    return sess.sid.hex


@d.add_method
@wrap_error
@check_type
@orm.db_session
def userSignIn(username: str, password: str):
    user = User.get_db(username=username)
    assert check_pw(password, user.password)
    Session.update_db(user.uid)
    sess = Session[user.uid]
    return sess.sid.hex


@d.add_method
@wrap_error
@check_type
def userSignOut(sid: str):
    sess = Session.get_db(sid=sid)
    Session.touch_db(sess.uid, 0, 0)


@d.add_method
@wrap_error
@check_sess
@check_type
def isAdmin(sid: str):
    sess = Session.get_db(sid=sid)
    return Admin.exists_db(uid=sess.uid)


@d.add_method
@wrap_error
@check_sess
@check_type
def isReader(sid: str):
    sess = Session.get_db(sid=sid)
    return Reader.exists_db(uid=sess.uid)


@d.add_method
@wrap_error
@check_user
@check_sess
@check_type
def addJournal(sid: str,
               name: str,
               issn: str,
               cnc: str,
               pdc: str,
               freq: str,
               addr: str,
               lang: str,
               hist: str,
               used: str):
    kwargs = locals()
    del kwargs['sid']
    return Journal.new_db(**kwargs)


@d.add_method
@wrap_error
@check_user
@check_sess
@check_type
def getJournal(sid: str,
               jid: Optional[int],
               name: Optional[str],
               issn: Optional[str],
               cnc: Optional[str],
               pdc: Optional[str],
               freq: Optional[str],
               addr: Optional[str],
               lang: Optional[str],
               hist: Optional[str],
               used: Optional[str]):
    kwargs = locals()
    del kwargs['sid']
    return Journal.select_db(**kwargs)
