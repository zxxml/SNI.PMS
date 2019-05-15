#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from enum import Enum

from spyne import ComplexModel, Integer, ServiceBase, Unicode, srpc

from db import Session, User, db_sql
from utils import hash_pw


class StatusModel(ComplexModel):
    """This class is designed as return value for every service.
    You should use a tuple simply rather than create it clearly.
    """
    status = Integer
    reason = Unicode


class Status(Enum):
    success = 0x0000
    # user related error
    username_409 = 0x1000  # username is conflict
    username_400 = 0x1001  # username doesn't exists
    password_400 = 0x1002  # password doesn't match
    # sess related error
    session_400 = 0x1000  # session doesn't exists
    session_403 = 0x1001  # session's user is forbidden

    @property
    def model(self):
        status = self.value
        reason = self.name
        return status, reason


class UserModel(ComplexModel):
    username = Unicode
    nickname = Unicode
    password = Unicode
    real_name = Unicode
    mail_addr = Unicode
    telephone = Unicode


# noinspection PyMethodParameters
class SNIWebService(ServiceBase):
    @srpc(UserModel, _returns=(str, StatusModel))
    def sign_in(user):
        user = User.new_db(user.username,
                           user.nickname,
                           hash_pw(user.password),
                           user.real_name,
                           user.mail_addr,
                           user.telephone)
        sess = Session.new_db(user.uid)
        return sess.sid.hex, Status.success.model

    # @staticmethod
    @srpc(UserModel, _returns=(str, StatusModel))
    def sign_up(user):
        user = User.get_db(username=user.username)
        Session.update_db(uid=user.uid)
        sess = Session.get_db(uid=user.uid)
        return sess.sid.hex, Status.success.model

    # @staticmethod
    @srpc(Unicode, _returns=StatusModel)
    def sign_out(sid):
        sess = Session.get_db(sid=sid)
        Session.touch_db(sess.uid, 0, 0)
        return Status.success.model


def mainloop():
    from spyne.application import Application
    from spyne.protocol.soap import Soap11
    from spyne.server.wsgi import WsgiApplication
    from wsgiref.simple_server import make_server
    app = Application([SNIWebService], 'spyne.examples.hello.http',
                      in_protocol=Soap11(validator='lxml'),
                      out_protocol=Soap11(),
                      )
    server = make_server('127.0.0.1', 8080, WsgiApplication(app))
    server.serve_forever()


if __name__ == '__main__':
    db_sql.bind('sqlite', ':memory:', create_db=True)
    # db_sql.bind('sqlite', 'sni.db', create_db=True)
    db_sql.generate_mapping(create_tables=True)
    mainloop()
