#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from enum import Enum
from wsgiref.simple_server import make_server

from spyne import (Application, Boolean, ComplexModel, Integer,
                   ModelBase, ServiceBase, String, rpc)
from spyne.protocol.soap import Soap12
from spyne.server.wsgi import WsgiApplication

from db import Administrator, Reader, Session, User, db_sql
from utils import check_pw, hash_pw

# ////////////////////////////////////////
#             Model Structures
# ////////////////////////////////////////


# make all model mandatory by default
# why spyne makes those damn twisted?
ModelBase.Attributes.nillable = False
ModelBase.Attributes.min_occurs = 1
ModelBase.Attributes.max_occurs = 1


class Status(Enum):
    success = 0x0000
    # user related error
    username_409 = 0x1000  # username is conflict
    username_400 = 0x1001  # username doesn't exists
    password_400 = 0x1002  # password doesn't match
    # sess related error
    session_400 = 0x2000  # session doesn't exists
    session_403 = 0x2001  # session's user is forbidden

    @property
    def model(self):
        status = self.value
        reason = self.name
        return status, reason


class StatusModel(ComplexModel):
    """This class is designed as return value for every service.
    You should use a tuple simply rather than create it clearly.
    """
    status = Integer
    reason = String


class UserModel(ComplexModel):
    """UserModel is the model of db.User, which means
    it has all attributes db.User has in spyne's way.
    """
    username = String
    nickname = String
    password = String
    real_name = String(min_occurs=0)
    mail_addr = String(min_occurs=0)
    telephone = String(min_occurs=0)


class JournalModel(ComplexModel):
    """JournalModel is the model of db.Journal, which means
    it has all attributes db.Journal has in spyne's way.
    """
    name = String
    issn = String
    cnc = String
    pdc = String
    freq = String
    addr = String
    lang = String
    hist = String
    used = String(min_occurs=0)


# ////////////////////////////////////////
#               Web Services
# ////////////////////////////////////////


class UserService(ServiceBase):
    @rpc(UserModel, _returns=(String, StatusModel))
    def signIn(self, user):
        user.password = hash_pw(user.password)
        user = User.new_db(**user.as_dict())
        sess = Session.new_db(user.uid)
        return sess.sid.hex, Status.success.model

    @rpc(String, String, _returns=(String, StatusModel))
    def signUp(self, username, password):
        if not User.exists_db(username=username):
            return '', Status.username_400.model
        user = User.get_db(username=username)
        if not check_pw(password, user.password):
            return '', Status.password_400.model
        Session.update_db(user.uid)
        sess = Session.get_db(uid=user.uid)
        return sess.sid.hex, Status.success.model

    @rpc(String, _returns=StatusModel)
    def signOut(self, sid):
        if not Session.exists_db(sid=sid):
            return Status.session_400.model
        sess = Session.get_db(sid=sid)
        Session.touch_db(sess.uid, 0, 0)
        return Status.success.model

    @rpc(String, _returns=(Boolean, StatusModel))
    def isAdministrator(self, sid):
        if not Session.exists_db(sid=sid):
            return False, Status.session_400.model
        sess = Session.get_db(sid=sid)
        flag = Administrator.exists_db(uid=sess.uid)
        return flag, Status.success.model

    @rpc(String, _returns=(Boolean, StatusModel))
    def isReader(self, sid):
        if not Session.exists_db(sid=sid):
            return False, Status.session_400.model
        sess = Session.get_db(sid=sid)
        flag = Reader.exists_db(uid=sess.uid)
        return flag, Status.success.model


class JournalService(ServiceBase):
    pass


# ////////////////////////////////////////
#           Customer Application
# ////////////////////////////////////////


class SNIApplication(Application):
    def __init__(self, services, tns, **kwargs):
        kwargs.setdefault('in_protocol', Soap12(validator='lxml'))
        kwargs.setdefault('out_protocol', Soap12())
        super().__init__(services, tns, 'SNIApplication', **kwargs)

    def serve_forever(self, host, port, **kwargs):
        wsgi_app = WsgiApplication(self, **kwargs)
        server = make_server(host, port, wsgi_app)
        server.serve_forever(0.5)


if __name__ == '__main__':
    db_sql.bind('sqlite', ':memory:', create_db=True)
    # db_sql.bind('sqlite', 'sni.db', create_db=True)
    db_sql.generate_mapping(create_tables=True)
    app = SNIApplication([UserService], 'SNI.PMS.SOAP')
    app.serve_forever('127.0.0.1', 8080)
