#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime, timedelta
from uuid import uuid1

from pony import orm

db = orm.Database()
config = ConfigParser()
config.read('sni.ini')


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
    db.Entity.delete(self)


@orm.db_session
def set_db(self, **kwargs):
    db.Entity.set(self, **kwargs)


db.Entity.delete_db = delete_db
db.Entity.set_db = set_db


class User(db.Entity, metaclass=EntityMeta):
    """User maintains the core information of the user.
    A.k.a the attrs of the user entity in the ER Diagram.
    """
    uid = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str, unique=True)
    nickname = orm.Required(str)
    password = orm.Required(str)
    real_name = orm.Optional(str)
    mail_addr = orm.Optional(str)
    telephone = orm.Optional(str)


class Administrator(User):
    """Administrator is a view of the User table.
    A.k.a all administrators in the source table.
    """
    pass


class Reader(User):
    """Reader is a view of the User table.
    A.k.a all readers in the source table.
    """
    pass


class Session(db.Entity, metaclass=EntityMeta):
    """Session maintains the core information of the session.
    A.k.a the attrs of the session entity in the ER Diagram.
    """
    uid = orm.PrimaryKey(int, auto=False)
    sid = orm.Required(str, unique=True)
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
        return uuid1(node, uid).hex


class Journal(db.Entity, metaclass=EntityMeta):
    jid = orm.PrimaryKey(int, auto=True)
    # name and some codes
    name = orm.Required(str)
    issn = orm.Required(str)
    cnc = orm.Optional(str)
    pdc = orm.Optional(str)
    # publication details
    freq = orm.Required(str)
    addr = orm.Required(str)
    lang = orm.Required(str)
    hist = orm.Required(str)
    used = orm.Optional(str)


class Subscription(db.Entity, metaclass=EntityMeta):
    jid = orm.Required(int)
    year = orm.Required(int)
    vol = orm.Required(int)
    iss = orm.Required(int)


class Article(db.Entity, metaclass=EntityMeta):
    aid = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    author = orm.Required(str)
    keyword_1 = orm.Optional(str)
    keyword_2 = orm.Optional(str)
    keyword_3 = orm.Optional(str)
    keyword_4 = orm.Optional(str)
    keyword_5 = orm.Optional(str)


class Borrow(db.Entity, metaclass=EntityMeta):
    uid = orm.Required(int)
    aid = orm.Required(int)
    borrow_date = orm.Required(datetime)
    expect_date = orm.Required(datetime)
    return_date = orm.Required(datetime)


if __name__ == '__main__':
    # db.bind('sqlite', ':memory:', create_db=True)
    db.bind('sqlite', 'sni.db', create_db=True)
    db.generate_mapping(create_tables=True)
