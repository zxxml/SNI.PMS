#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from enum import Enum

from spyne import DateTime, Integer, Unicode
from spyne.model import ComplexModel, ModelBase

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
    status = Integer(values=Status._value2member_map_.keys())
    reason = Unicode(values=Status._member_map_.keys())


class UserModel(ComplexModel):
    """UserModel is the model of db.User, which means
    it has all attributes db.User has in spyne's way.
    """
    username = Unicode
    nickname = Unicode
    password = Unicode
    real_name = Unicode(min_occurs=0)
    mail_addr = Unicode(min_occurs=0)
    telephone = Unicode(min_occurs=0)


class JournalModel(ComplexModel):
    """JournalModel is the model of db.Journal, which means
    it has all attributes db.Journal has in spyne's way.
    """
    name = Unicode
    issn = Unicode
    cnc = Unicode
    pdc = Unicode
    freq = Unicode
    addr = Unicode
    lang = Unicode
    hist = Unicode
    used = Unicode(min_occurs=0)


class ArticleModel(ComplexModel):
    """ArticleModel is the model of db.Article, which means
    it has all attributes db.Article has in spyne's way.
    """
    jid = Integer
    title = Unicode
    author = Unicode
    content = Unicode
    keyword_1 = Unicode(min_occurs=0)
    keyword_2 = Unicode(min_occurs=0)
    keyword_3 = Unicode(min_occurs=0)
    keyword_4 = Unicode(min_occurs=0)
    keyword_5 = Unicode(min_occurs=0)


class SubscriptionModel(ComplexModel):
    jid = Integer
    year = Integer


class StorageModel(ComplexModel):
    jid = Integer
    year = Integer
    vol = Integer
    iss = Integer


class BorrowModel(ComplexModel):
    uid = Integer
    jid = Integer
    borrow_date = DateTime
    expect_date = DateTime
    return_date = DateTime(min_occurs=0)
