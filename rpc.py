#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from uuid import uuid1

from jsonrpc import Dispatcher
from pony import orm

from db import Admin, Journal, Reader, Storage, Subs, User
from utils import check_admin, check_pw, check_user, clean_locals, hash_pw, new_expire

__all__ = ['d']
d = Dispatcher()


@d.add_method
@orm.db_session
def adminSignUp(username: str,
                nickname: str,
                password: str,
                foreName: str = None,
                lastName: str = None,
                mailAddr: str = None,
                phoneNum: str = None):
    sessId = uuid1().hex
    expire = new_expire()
    password = hash_pw(password)
    user = Admin.new(**locals())
    return user.sessId


@d.add_method
@orm.db_session
def readerSignUp(username: str,
                 nickname: str,
                 password: str,
                 foreName: str = None,
                 lastName: str = None,
                 mailAddr: str = None,
                 phoneNum: str = None):
    sessId = uuid1().hex
    expire = new_expire()
    password = hash_pw(password)
    user = Reader.new(**locals())
    return user.sessId


@d.add_method
@orm.db_session
def userSignIn(username: str,
               password: str):
    user = User.get(username=username)
    assert check_pw(password, user.password)
    user.sessId = uuid1().hex
    user.expire = new_expire()
    return user.sessId


@d.add_method
@orm.db_session
def userSignOut(sessId: str):
    user = User.get(sessId=sessId)
    user.expire = new_expire(0, 0)


@d.add_method
@orm.db_session
def getUser(sessId: str):
    user = User.get(sessId=sessId)
    return user.to_dict() if user else None


@d.add_method
@orm.db_session
def setUser(sessId: str,
            nickname: str = None,
            password: str = None,
            foreName: str = None,
            lastName: str = None,
            mailAddr: str = None,
            phoneNum: str = None):
    password = password and hash_pw(password)
    User.get(sessId=sessId).set(**locals())


@d.add_method
@orm.db_session
def delUser(sessId: str):
    User.get(sessId=sessId).delete()


@d.add_method
@orm.db_session
def addJournal(sessId: str,
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
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    journal = Journal.new(**kwargs)
    return journal.jourId


@d.add_method
@orm.db_session
def getJournal(sessId: str,
               jourId: int = None,
               issn: str = None,
               cnc: str = None,
               pdc: str = None):
    assert check_user(sessId)
    kwargs = clean_locals(locals())
    result = Journal.select(**kwargs)
    return result[0] if result else None


@d.add_method
@orm.db_session
def getJournals(sessId: str,
                jourId: int = None,
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
    assert check_user(sessId)
    kwargs = clean_locals(locals())
    return Journal.select(**kwargs)


@d.add_method
@orm.db_session
def setJournal(sessId: str,
               jourId: int,
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
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    Journal[jourId].set(**kwargs)


@d.add_method
@orm.db_session
def delJournal(sessId: str,
               jourId: int):
    assert check_admin(sessId)
    Journal[jourId].delete()


@d.add_method
@orm.db_session
def addSubs(sessId: str,
            jourId: int,
            year: int):
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    subs = Subs.new(**kwargs)
    return subs.subsId


@d.add_method
@orm.db_session
def getSubs(sessId: str,
            subsId: int = None,
            jourId: int = None,
            year: int = None):
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    result = Subs.select(**kwargs)
    return result[0] if result else None


@d.add_method
@orm.db_session
def getSubses(sessId: str,
              jourId: int = None,
              year: int = None):
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    return Subs.select(**kwargs)


@d.add_method
@orm.db_session
def setSubs(sessId: str,
            subsId: int,
            jourId: int = None,
            year: int = None):
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    Subs[subsId].set(**kwargs)


@d.add_method
@orm.db_session
def delSubs(sessId: str,
            subsId: int):
    assert check_admin(sessId)
    Subs[subsId].delete()


@d.add_method
@orm.db_session
def addStorage(sessId: str,
               subsId: int,
               vol: int,
               iss: int):
    assert check_admin(sessId)
    kwargs = clean_locals(locals())
    storage = Storage.new(**kwargs)
    return storage.stoId


@d.add_method
@orm.db_session
def getStorage(sessId: str,
               stoId: int = None,
               subsId: int = None,
               vol: int = None,
               iss: int = None):
    assert check_user(sessId)
    kwargs = clean_locals(locals())
    result = Storage.select(**kwargs)
    return result[0] if result else None


@d.add_method
@orm.db_session
def getStorages():
    pass


@d.add_method
@orm.db_session
def setStorage():
    pass


@d.add_method
@orm.db_session
def delStorage():
    pass


@d.add_method
@orm.db_session
def addArticle():
    pass


@d.add_method
@orm.db_session
def getArticle():
    pass


@d.add_method
@orm.db_session
def getArticles():
    pass


@d.add_method
@orm.db_session
def setArticle():
    pass


@d.add_method
@orm.db_session
def delArticle():
    pass


@d.add_method
@orm.db_session
def addBorrow():
    pass


@d.add_method
@orm.db_session
def getBorrow():
    pass


@d.add_method
@orm.db_session
def getBorrows():
    pass


@d.add_method
@orm.db_session
def setBorrow():
    pass


@d.add_method
@orm.db_session
def delBorrow():
    pass
