#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from uuid import uuid1

from jsonrpc import Dispatcher
from pony import orm

from db import Admin, Journal, Reader, Subs, User
from utils import check_admin, check_pw, check_user, clean_locals, hash_pw, new_expires

__all__ = ['d']
d = Dispatcher()


@d.add_method
@orm.db_session
def adminSignUp(username: str,
                nickname: str,
                password: str,
                fore_name: str = None,
                last_name: str = None,
                mail_addr: str = None,
                phone_num: str = None):
    sess_id = uuid1().hex
    expires = new_expires()
    password = hash_pw(password)
    user = Admin.new(**locals())
    return user.sess_id


@d.add_method
@orm.db_session
def readerSignUp(username: str,
                 nickname: str,
                 password: str,
                 fore_name: str = None,
                 last_name: str = None,
                 mail_addr: str = None,
                 phone_num: str = None):
    sess_id = uuid1().hex
    expires = new_expires()
    password = hash_pw(password)
    user = Reader.new(**locals())
    return user.sess_id


@d.add_method
@orm.db_session
def userSignIn(username: str,
               password: str):
    user = User.get(username=username)
    assert check_pw(password, user.password)
    user.sess_id = uuid1().hex
    user.expires = new_expires()
    return user.sess_id


@d.add_method
@orm.db_session
def userSignOut(sess_id: str):
    user = User.get(sess_id=sess_id)
    user.expires = new_expires(0, 0)


@d.add_method
@orm.db_session
def getUser(sess_id: str):
    user = User.get(sess_id=sess_id)
    return user.to_dict() if user else None


@d.add_method
@orm.db_session
def setUser(sess_id: str,
            nickname: str = None,
            fore_name: str = None,
            last_name: str = None,
            mail_addr: str = None,
            phone_num: str = None):
    User.get(sess_id=sess_id).set(**locals())


@d.add_method
@orm.db_session
def delUser(sess_id: str):
    User.get(sess_id=sess_id).delete()


@d.add_method
@orm.db_session
def addJournal(sess_id: str,
               name: str,
               lang: str,
               hist: str,
               freq: str,
               issn: str,
               cnc: str,
               pdc: str,
               used: str = None,
               addr: str = None,
               org: str = None,
               pub: str = None):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    journal = Journal.new(**kwargs)
    return journal.jour_id


@d.add_method
@orm.db_session
def getJournal(sess_id: str,
               jour_id: int = None,
               issn: str = None,
               cnc: str = None,
               pdc: str = None):
    assert check_user(sess_id)
    kwargs = clean_locals(locals())
    result = Journal.select(**kwargs)
    return result[0] if result else None


@d.add_method
@orm.db_session
def getJournals(sess_id: str,
                jour_id: int = None,
                name: str = None,
                lang: str = None,
                hist: str = None,
                freq: str = None,
                issn: str = None,
                cnc: str = None,
                pdc: str = None,
                used: str = None,
                addr: str = None,
                org: str = None,
                pub: str = None):
    assert check_user(sess_id)
    kwargs = clean_locals(locals())
    return Journal.select(**kwargs)


@d.add_method
@orm.db_session
def setJournal(sess_id: str,
               jour_id: int,
               name: str = None,
               lang: str = None,
               hist: str = None,
               freq: str = None,
               issn: str = None,
               cnc: str = None,
               pdc: str = None,
               used: str = None,
               addr: str = None,
               org: str = None,
               pub: str = None):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    Journal[jour_id].set(**kwargs)


@d.add_method
@orm.db_session
def delJournal(sess_id: str,
               jour_id: int):
    assert check_admin(sess_id)
    Journal[jour_id].delete()


@d.add_method
@orm.db_session
def addSubs(sess_id: str,
            jour_id: int,
            year: int):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    subs = Subs.new(**kwargs)
    return subs.subs_id


@d.add_method
@orm.db_session
def getSubs(sess_id: str,
            subs_id: int,
            jour_id: int,
            year: int):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    result = Subs.select(**kwargs)
    return result[0] if result else None


@d.add_method
@orm.db_session
def getSubses(sess_id: str,
              jour_id: int = None,
              year: int = None):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    return Subs.select(**kwargs)


@d.add_method
@orm.db_session
def setSubs(sess_id: str,
            subs_id: int,
            jour_id: int = None,
            year: int = None):
    assert check_admin(sess_id)
    kwargs = clean_locals(locals())
    Subs[subs_id].set(**kwargs)


@d.add_method
@orm.db_session
def delSubs(sess_id: str,
            subs_id: int):
    assert check_admin(sess_id)
    Subs[subs_id].delete()


def addArticle(sess_id: str):
    pass
