#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import Optional

from jsonrpc import Dispatcher
from pony import orm
from typeguard import typechecked

from sni.db import Admin, Reader, Session, User
from sni.utils import Fault, catch_errors, check_permit, check_pw, check_session, hash_pw

__all__ = ['d']
d = Dispatcher()


@d.add_method
@catch_errors
@typechecked
def adminSignUp(username: str,
                nickname: str,
                password: str,
                real_name: Optional[str],
                mail_addr: Optional[str],
                telephone: Optional[str]):
    try:
        password = hash_pw(password)
        user = Admin.new_db(**locals())
        sess = Session.new_db(user.uid)
        return sess.sid.hex
    except orm.TransactionIntegrityError as e:
        raise Fault.user_409(str(e))


@d.add_method
@catch_errors
@typechecked
def readerSignUp(username: str,
                 nickname: str,
                 password: str,
                 real_name: Optional[str],
                 mail_addr: Optional[str],
                 telephone: Optional[str]):
    try:
        password = hash_pw(password)
        user = Reader.new_db(**locals())
        sess = Session.new_db(user.uid)
        return sess.sid.hex
    except orm.TransactionIntegrityError as e:
        raise Fault.user_409(str(e))


@d.add_method
@catch_errors
@typechecked
@orm.db_session
def userSignIn(username: str, password: str):
    try:
        assert User.exists_db(username=username)
        user = User.get_db(username=username)
        assert check_pw(password, user.password)
        Session.update_db(user.uid)
        sess = Session[user.uid]
        return sess.sid.hex
    except AssertionError as e:
        raise Fault.user_400(str(e))


@d.add_method
@catch_errors
@check_session
@typechecked
@orm.db_session
def userSignOut(sid: str):
    sess = Session.get_db(sid=sid)
    Session.touch_db(sess.uid, 0, 0)


@d.add_method
@catch_errors
@check_session
@typechecked
@orm.db_session
def isAdmin(sid: str):
    sess = Session.get_db(sid=sid)
    return Admin.exists_db(uid=sess.uid)


@d.add_method
@catch_errors
@check_session
@typechecked
@orm.db_session
def isReader(sid: str):
    sess = Session.get_db(sid=sid)
    return Reader.exists_db(uid=sess.uid)


@d.add_method
@catch_errors
@check_permit
@check_session
@typechecked
@orm.db_session
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
    pass


@d.add_method
@catch_errors
@check_permit
@check_session
@typechecked
@orm.db_session
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
    pass
