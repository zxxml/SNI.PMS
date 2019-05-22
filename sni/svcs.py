#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import Optional

from jsonrpc import Dispatcher
from pony import orm
from typeguard import typechecked

from sni.db import Admin, Article, Journal, Reader, User
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
        return user.session.hex
    except orm.TransactionIntegrityError:
        message = 'Username conflict.'
        raise Fault.USER_409(message)


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
        return user.session.hex
    except orm.TransactionIntegrityError:
        message = 'Username conflict.'
        raise Fault.USER_409(message)


@d.add_method
@catch_errors
@typechecked
def userSignIn(username: str, password: str):
    try:
        # "Incorrect username or password." is bullshit
        # We're glad to provide more details for users
        assert User.exists_db(username=username), 'username'
        user = User.get_db(username=username)
        assert check_pw(password, user.password), 'password'
        User.update_session(user.uid)
        return user.session.hex
    except AssertionError as e:
        message = 'Incorrect %s.' % e.args
        raise Fault.USER_400(message)


@d.add_method
@catch_errors
@check_session
@typechecked
def userSignOut(sid: str):
    user = User.get_db(session=sid)
    User.touch_session(user.uid, 0, 0)


@d.add_method
@catch_errors
@check_session
@typechecked
def isAdmin(sid: str):
    # just check the Admin view
    return Admin.exists_sid(sid)


@d.add_method
@catch_errors
@check_session
@typechecked
def isReader(sid: str):
    # just check the Reader view
    return Reader.exists_sid(sid)


@d.add_method
@catch_errors
@check_permit
@typechecked
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
    try:
        kwargs = locals()
        del kwargs['sid']
        return Journal.new_db(**kwargs)
    except orm.core.TransactionIntegrityError:
        message = 'Journal info conflict.'
        raise Fault.JOURNAL_409(message)


@d.add_method
@catch_errors
@check_permit
@typechecked
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


@d.add_method
@catch_errors
@check_permit
@typechecked
def addArticle(sid: str,
               rid: int,
               title: str,
               author: str,
               content: str,
               keyword_1: str,
               keyword_2: str,
               keyword_3: str,
               keyword_4: str,
               keyword_5: str):
    try:
        kwargs = locals()
        del kwargs['sid']
        Article.new_db(**kwargs)
    except orm.TransactionIntegrityError:
        message = 'Journal not in stock.'
        raise Fault.ARTICLE_412(message)


@d.add_method
@catch_errors
@check_permit
@typechecked
def getArticle(sid: str,
               aid: int,
               rid: int,
               title: str,
               author: str,
               content: str,
               keyword_1: str,
               keyword_2: str,
               keyword_3: str,
               keyword_4: str,
               keyword_5: str):
    kwargs = locals()
    del kwargs['sid']
    return Article.select_db(**kwargs)


@d.add_method
@catch_errors
@check_permit
@typechecked
def addSubs(sid: str,
            year: int,
            vol: int,
            iss: int,
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


@d.add_method
@catch_errors
@check_permit
@typechecked
def getSubs(sid: str,
            jid: Optional[int],
            year: Optional[int],
            vol: Optional[int],
            iss: Optional[int]):
    pass
