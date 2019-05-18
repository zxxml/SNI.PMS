#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from spyne import rpc
from spyne.model import Boolean, Unicode
from spyne.service import ServiceBase

from sni.db import Admin, Reader, Session, User
from sni.mods import Status, StatusModel, UserModel
from sni.utils import check_pw, hash_pw


class UserService(ServiceBase):
    @rpc(UserModel, _returns=(Unicode, StatusModel))
    def signUpAdmin(self, user):
        user.password = hash_pw(user.password)
        user = Admin.new_db(**user.as_dict())
        sess = Session.new_db(user.uid)
        return sess.sid.hex, Status.success.model

    @rpc(UserModel, _returns=(Unicode, StatusModel))
    def signUpReader(self, user):
        user.password = hash_pw(user.password)
        user = Reader.new_db(**user.as_dict())
        sess = Session.new_db(user.uid)
        return sess.sid.hex, Status.success.model

    @rpc(Unicode, Unicode, _returns=(Unicode, StatusModel))
    def signIn(self, username, password):
        if not User.exists_db(username=username):
            return '', Status.username_400.model
        user = User.get_db(username=username)
        if not check_pw(password, user.password):
            return '', Status.password_400.model
        Session.update_db(user.uid)
        sess = Session.get_db(uid=user.uid)
        return sess.sid.hex, Status.success.model

    @rpc(Unicode, _returns=StatusModel)
    def signOut(self, sid):
        if not Session.exists_db(sid=sid):
            return Status.session_400.model
        sess = Session.get_db(sid=sid)
        Session.touch_db(sess.uid, 0, 0)
        return Status.success.model

    @rpc(Unicode, _returns=(Boolean, StatusModel))
    def isAdmin(self, sid):
        if not Session.exists_db(sid=sid):
            return False, Status.session_400.model
        sess = Session.get_db(sid=sid)
        flag = Admin.exists_db(uid=sess.uid)
        return flag, Status.success.model

    @rpc(Unicode, _returns=(Boolean, StatusModel))
    def isReader(self, sid):
        if not Session.exists_db(sid=sid):
            return False, Status.session_400.model
        sess = Session.get_db(sid=sid)
        flag = Reader.exists_db(uid=sess.uid)
        return flag, Status.success.model


class SubsService(ServiceBase):
    pass


class StorageService(ServiceBase):
    pass


class ArticleService(ServiceBase):
    pass


class SearchService(ServiceBase):
    pass


class BorrowService(ServiceBase):
    pass
