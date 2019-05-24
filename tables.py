#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from datetime import date, datetime

from pony import orm


class EntityMeta(orm.core.EntityMeta):
    @staticmethod
    def clean_kwargs(kwargs):
        return {k: kwargs[k] for k in kwargs
                if kwargs[k] is not None}

    @orm.db_session
    def insert(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return cls(*args, **kwargs)

    @orm.db_session
    def exists(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().exists(*args, **kwargs)

    @orm.db_session
    def get(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().get(*args, **kwargs)

    @orm.db_session
    def select(cls, *args, **kwargs):
        if kwargs:
            kwargs = cls.clean_kwargs(kwargs)
            return super().select().filter(**kwargs)[:]
        return super().select(*args)[:]


@orm.db_session
def delete_db(self):
    db.Entity.delete_db(self)


@orm.db_session
def set_db(self, **kwargs):
    db.Entity.set_db(self, **kwargs)


db = orm.Database()
db.Entity.delete_db = db.Entity.delete
db.Entity.set_db = db.Entity.set
db.Entity.delete = delete_db
db.Entity.set = set_db


class User(db.Entity, metaclass=EntityMeta):
    user_id = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str, unique=True)
    nickname = orm.Required(str)
    password = orm.Required(str)
    first_name = orm.Optional(str)
    last_name = orm.Optional(str)
    email_address = orm.Optional(str)
    phone_number = orm.Optional(str)
    session_id = orm.Required(str)
    expire_time = orm.Required(datetime)


class Administrator(User): pass


class Reader(User): pass


class Journal(db.Entity, metaclass=EntityMeta):
    journal_id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str)
    language = orm.Required(str)
    history = orm.Required(str)
    host = orm.Required(str)
    publisher = orm.Required(str)
    used_name = orm.Optional(str)
    frequency = orm.Required(str)
    issn = orm.Required(str, unique=True)
    cn = orm.Required(str, unique=True)
    pdc = orm.Required(str, unique=True)


class Subscription(db.Entity, metaclass=EntityMeta):
    subscription_id = orm.PrimaryKey(int, auto=True)
    journal_id = orm.Required(int)
    year = orm.Required(int)
    orm.composite_key(journal_id, year)


class Storage(db.Entity, metaclass=EntityMeta):
    storage_id = orm.PrimaryKey(int, auto=True)
    journal_id = orm.Required(int)
    year = orm.Required(int)
    volume = orm.Required(int)
    issue = orm.Required(int)
    orm.composite_key(journal_id, year, volume, issue)


class Article(db.Entity, metaclass=EntityMeta):
    article_id = orm.PrimaryKey(int, auto=True)
    storage_id = orm.Required(int)
    page_number = orm.Required(int)
    title = orm.Required(str)
    author = orm.Required(str)
    content = orm.Required(str)
    keyword1 = orm.Optional(str)
    keyword2 = orm.Optional(str)
    keyword3 = orm.Optional(str)
    keyword4 = orm.Optional(str)
    keyword5 = orm.Optional(str)


class Borrowing(db.Entity, metaclass=EntityMeta):
    borrowing_id = orm.PrimaryKey(int, auto=True)
    user_id = orm.Required(int)
    storage_id = orm.Required(int)
    borrow_date = orm.Required(date)
    agreed_date = orm.Required(date)
    return_date = orm.Optional(date)


def bind_sqlite(filename=':memory:'):
    db.bind('sqlite', filename, create_db=True)
    db.generate_mapping(create_tables=True)
    with orm.db_session:
        # db.execute('PRAGMA synchronous = OFF')
        db.execute('PRAGMA journal_mode = WAL')
