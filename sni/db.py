#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime, timedelta
from uuid import UUID, uuid1

from pony import orm

db_sql = orm.Database()
config = ConfigParser()
config.read('./sni.ini')


class EntityMeta(orm.core.EntityMeta):
    """EntityMeta wraps common operations in the session with the suffix "db".
    You could manage the session by yourself since only the out-scope one works.
    """

    @orm.db_session
    def new_db(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @orm.db_session
    def exists_db(cls, *args, **kwargs):
        return cls.exists(*args, **kwargs)

    @orm.db_session
    def get_db(cls, *args, **kwargs):
        return cls.get(*args, **kwargs)

    @orm.db_session
    def select_db(cls, *args):
        return cls.select(*args)


@orm.db_session
def delete_db(self):
    db_sql.Entity.delete(self)


@orm.db_session
def set_db(self, **kwargs):
    db_sql.Entity.set(self, **kwargs)


db_sql.Entity.delete_db = delete_db
db_sql.Entity.set_db = set_db


class User(db_sql.Entity, metaclass=EntityMeta):
    """User maintains the core information of the user.
    A.k.a the attrs of the user entity in the ER Diagram.
    """
    uid = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str, unique=True, index=True)
    nickname = orm.Required(str)
    password = orm.Required(str)
    real_name = orm.Optional(str)
    mail_addr = orm.Optional(str)
    telephone = orm.Optional(str)


class Admin(User):
    """Admin is a view of the User table.
    A.k.a all admins in the source table.
    """
    pass


class Reader(User):
    """Reader is a view of the User table.
    A.k.a all readers in the source table.
    """
    pass


class Session(db_sql.Entity, metaclass=EntityMeta):
    """Session maintains the core information of the session.
    A.k.a the attrs of the session entity in the ER Diagram.
    """
    uid = orm.PrimaryKey(int, auto=False)
    sid = orm.Required(UUID, unique=True, index=True)
    expires = orm.Required(datetime)

    @staticmethod
    @orm.db_session
    def new_db(uid, sid=None, days=0, hours=12):
        sid = sid or Session.new_sid(uid)
        length = timedelta(days=days, hours=hours)
        expires = datetime.now() + length
        return Session(uid=uid, sid=sid, expires=expires)

    @staticmethod
    @orm.db_session
    def update_db(uid, sid=None, days=0, hours=12):
        sid = sid or Session.new_sid(uid)
        Session.touch_db(uid, days, hours)
        Session[uid] and Session[uid].set(sid=sid)

    @staticmethod
    @orm.db_session
    def touch_db(uid, days, hours):
        length = timedelta(days=days, hours=hours)
        kwargs = {'expires': datetime.now() + length}
        Session[uid] and Session[uid].set(**kwargs)

    @staticmethod
    def new_sid(uid):
        node = int(config['uuid']['node'], 16)
        return uuid1(node, uid)


class Journal(db_sql.Entity, metaclass=EntityMeta):
    """Journal maintains the core information of the journal.
    A.k.a the attrs of the journal entity in the ER Diagram.
    """
    jid = orm.PrimaryKey(int, auto=True)
    # name and some codes
    name = orm.Required(str)
    issn = orm.Required(str, unique=True)
    cnc = orm.Required(str, unique=True)
    pdc = orm.Required(str, unique=True)
    # publication details
    freq = orm.Required(str)
    addr = orm.Required(str)
    lang = orm.Required(str)
    hist = orm.Required(str)
    used = orm.Optional(str)


class Article(db_sql.Entity, metaclass=EntityMeta):
    """Article maintains the core information of the article.
    A.k.a the attrs of the article entity in the ER Diagram.
    """
    # primary and foreign key
    aid = orm.PrimaryKey(int, auto=True)
    jid = orm.Required(int)
    # the most important info
    title = orm.Required(str)
    author = orm.Required(str)
    content = orm.Required(str)
    # list all five keywords
    keyword_1 = orm.Optional(str)
    keyword_2 = orm.Optional(str)
    keyword_3 = orm.Optional(str)
    keyword_4 = orm.Optional(str)
    keyword_5 = orm.Optional(str)


class Subs(db_sql.Entity, metaclass=EntityMeta):
    """Subs maintains the core information of the subs.
    A.k.a the attrs of the subs relationship in the ER Diagram.
    """
    jid = orm.Required(int)
    year = orm.Required(int)
    orm.PrimaryKey(jid, year)


class Storage(db_sql.Entity, metaclass=EntityMeta):
    """Storage maintains the core information of the storage.
    A.k.a the attrs of the storage relationship in the ER Diagram.
    """
    jid = orm.Required(int)
    year = orm.Required(int)
    vol = orm.Required(int)
    iss = orm.Required(int)
    orm.PrimaryKey(jid, year, vol, iss)


class Borrow(db_sql.Entity, metaclass=EntityMeta):
    uid = orm.Required(int)
    jid = orm.Required(int)
    borrow_date = orm.Required(datetime)
    expect_date = orm.Required(datetime)
    return_date = orm.Optional(datetime)
    orm.PrimaryKey(uid, jid, borrow_date)


def bind_sqlite(filename=':memory:'):
    db_sql.bind('sqlite', filename, create_db=True)
    db_sql.generate_mapping(create_tables=True)
