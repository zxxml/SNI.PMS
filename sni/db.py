#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from datetime import datetime

from pony import orm


class EntityMeta(orm.core.EntityMeta):
    @staticmethod
    def clean_kwargs(kwargs):
        return {k: kwargs[k] for k in kwargs
                if kwargs[k] is not None}

    def __getitem__(self, key):
        if key is None: return None
        return super().__getitem__(key)

    @orm.db_session
    def new(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        result = cls(*args, **kwargs)
        return db.commit() or result

    @orm.db_session
    def exists(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().exists(*args, **kwargs)

    @orm.db_session
    def get(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().get(*args, **kwargs)

    @orm.db_session
    def select(cls, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().select().filter(**kwargs)[:]

    @staticmethod
    @orm.db_session
    def delete_db(self, **kwargs):
        kwargs = EntityMeta.clean_kwargs(kwargs)
        self.delete_db(**kwargs)

    @staticmethod
    @orm.db_session
    def set_db(self, **kwargs):
        kwargs = EntityMeta.clean_kwargs(kwargs)
        self.set_db(**kwargs)


db = orm.Database()
db.Entity.delete_db = db.Entity.delete
db.Entity.set_db = db.Entity.set
db.Entity.delete = EntityMeta.delete_db
db.Entity.set = EntityMeta.set_db


def bind_sqlite(filename):
    db.bind('sqlite', filename, create_db=True)
    db.generate_mapping(create_tables=True)
    with orm.db_session:
        # db.execute('PRAGMA synchronous = OFF')
        db.execute('PRAGMA journal_mode = WAL')


class User(db.Entity, metaclass=EntityMeta):
    username = orm.Required(str, unique=True)
    nickname = orm.Required(str, unique=True)
    password = orm.Required(str)
    forename = orm.Optional(str)
    lastname = orm.Optional(str)
    mailaddr = orm.Optional(str)
    phonenum = orm.Optional(str)
    session  = orm.Optional('Session', cascade_delete=True)
    borrows  = orm.Set('Borrow', cascade_delete=True)
class Admin(User): pass
class Reader(User): pass


class Session(db.Entity, metaclass=EntityMeta):
    sessionid = orm.Required(str, unique=True)
    shelflife = orm.Required(datetime)
    user      = orm.Required('User')


class Journal(db.Entity, metaclass=EntityMeta):
    name = orm.Required(str)
    issn = orm.Required(str)
    isbn = orm.Required(str)
    post = orm.Required(str)
    host = orm.Required(str)
    addr = orm.Required(str)
    freq = orm.Required(str)
    lang = orm.Required(str)
    hist = orm.Optional(str)
    used = orm.Optional(str)
    subscribe = orm.Set('Subscribe')


class Subscribe(db.Entity, metaclass=EntityMeta):
    year    = orm.Required(int)
    journal = orm.Required('Journal')
    storage = orm.Set('Storage')


class Storage(db.Entity, metaclass=EntityMeta):
    volume    = orm.Required(int)
    number    = orm.Required(int)
    subscribe = orm.Required('Subscribe')
    articles  = orm.Set('Article')
    borrows   = orm.Set('Borrow')


class Article(db.Entity, metaclass=EntityMeta):
    title    = orm.Required(str)
    author   = orm.Required(str)
    pagenum  = orm.Required(str)
    keyword1 = orm.Optional(str)
    keyword2 = orm.Optional(str)
    keyword3 = orm.Optional(str)
    keyword4 = orm.Optional(str)
    keyword5 = orm.Optional(str)
    storage  = orm.Required('Storage')


class Borrow(db.Entity, metaclass=EntityMeta):
    borrowtime = orm.Required(datetime)
    agreedtime = orm.Required(datetime)
    returntime = orm.Optional(datetime)
    user       = orm.Required('User')
    storage    = orm.Required('Storage')
