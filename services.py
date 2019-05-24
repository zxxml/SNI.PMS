#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from spyne import Boolean, String
from spyne import Fault
from spyne import ServiceBase, rpc

from tables import Administrator, User
from models import UserModel
from utilities import hash_pw


class UserService(ServiceBase):
    @rpc(UserModel, _returns=String)
    def admin_sign_up(self, user_model: UserModel):
        if not user_model.username:
            raise Fault(faultstring='Missing attributes: %s.' % 'username')
        if not user_model.nickname:
            raise Fault(faultstring='Missing attributes: %s.' % 'nickname')
        if not user_model.password:
            raise Fault(faultstring='Missing attributes: %s.' % 'password')
        if User.exists(username=user_model.username):
            raise Fault(faultstring='Username conflict.')
        user_model.password = hash_pw(user_model.password)
        user = Administrator.insert(**user_model.as_dict('user_id'))
        return user.session_id

    @rpc(UserModel, _returns=String)
    def reader_sign_up(self, user_model):
        pass

    @rpc(UserModel, _returns=String)
    def user_sign_in(self, user_model):
        pass

    @rpc(String, _returns=UserModel)
    def get_user(self, session_id):
        pass

    @rpc(String, UserModel, _returns=UserModel)
    def set_user(self, session_id, user_model):
        pass

    @rpc(String, _returns=Boolean)
    def is_admin(self, session_id):
        pass

    @rpc(String, _returns=Boolean)
    def is_reader(self, session_id):
        pass
