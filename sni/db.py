#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime, timedelta
from secrets import randbelow
from uuid import UUID, uuid1

from pony import orm

db_sql = orm.Database()
config = ConfigParser()
config.read('./sni.ini')


class EntityMeta(orm.core.EntityMeta):
    """EntityMeta wraps common operations in the session with the suffix "db".
    You could manage the session by yourself since only the out-scope one works.
    """
    @staticmethod
    def clean_kwargs(kwargs):
        return {k: kwargs[k] for k in kwargs
                if kwargs[k] is not None}

    @orm.db_session
    def new_db(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return cls(*args, **kwargs)

    @orm.db_session
    def exists_db(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return cls.exists(*args, **kwargs)

    @orm.db_session
    def get_db(cls, *args, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return cls.get(*args, **kwargs)

    @orm.db_session
    def select_db(cls, *args, **kwargs):
        if kwargs:
            kwargs = cls.clean_kwargs(kwargs)
            return cls.select().filter(**kwargs)[:]
        return cls.select(*args)[:]


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
    session = orm.Required(UUID, unique=True, index=True)
    expires = orm.Required(datetime)

    @classmethod
    @orm.db_session
    def new_db(cls, days=0, hours=12, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        session = cls.new_session()
        expires = cls.new_expires(days, hours)
        return cls(session=session, expires=expires, **kwargs)

    @classmethod
    @orm.db_session
    def exists_sid(cls, sid):
        """Whether the session exists."""
        return cls.exists(session=sid)

    @classmethod
    @orm.db_session
    def get_sid(cls, sid):
        """Get a user by session."""
        return cls.get(session=sid)

    @classmethod
    @orm.db_session
    def update_session(cls, uid, days=0, hours=12):
        session = cls.new_session()
        expires = cls.new_expires(days, hours)
        kwargs = {'session': session, 'expires': expires}
        cls[uid].set(session=session, expires=expires)

    @classmethod
    @orm.db_session
    def touch_session(cls, uid, days=0, hours=12):
        expires = cls.new_expires(days, hours)
        cls[uid].set(expires=expires)

    @staticmethod
    def new_session():
        node = int(config['uuid']['node'], 16)
        # uuid1 accepts integer below 16384
        return uuid1(node, randbelow(16384))

    @staticmethod
    def new_expires(days=0, hours=12):
        length = timedelta(days=days, hours=hours)
        return datetime.now() + length


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


class Journal(db_sql.Entity, metaclass=EntityMeta):
    """Journal maintains the core information of the journal.
    A.k.a the attrs of the journal entity in the ER Diagram.
    """
    jid = orm.PrimaryKey(int, auto=True)
    # name and some codes
    name = orm.Required(str, index=True)
    issn = orm.Required(str, unique=True)
    cnc = orm.Required(str, unique=True)
    pdc = orm.Required(str, unique=True)
    # publication details
    freq = orm.Required(str)
    addr = orm.Required(str)
    lang = orm.Required(str)
    hist = orm.Required(str)
    used = orm.Optional(str)
    # foreign key constraints
    repo = orm.Set('Repository')
    subs = orm.Set('Subscription')


class Repository(db_sql.Entity, metaclass=EntityMeta):
    """Repository maintains the core information of the repository.
    A.k.a the attrs of the repository entity in the ER Diagram.
    """
    rid = orm.PrimaryKey(int)
    jid = orm.Required(Journal)
    year = orm.Required(int)
    vol = orm.Required(int)
    iss = orm.Required(int)
    # foreign key constraints
    art = orm.Set('Article')
    bor = orm.Set('Borrowing')


class Article(db_sql.Entity, metaclass=EntityMeta):
    """Article maintains the core information of the article.
    A.k.a the attrs of the article entity in the ER Diagram.
    """
    # primary and foreign key
    aid = orm.PrimaryKey(int, auto=True)
    rid = orm.Required(Repository)
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


class Subscription(db_sql.Entity, metaclass=EntityMeta):
    """Subscription maintains the core information of the subscription.
    A.k.a the attrs of the subscription relationship in the ER Diagram.
    """
    sid = orm.PrimaryKey(int, auto=True)
    jid = orm.Required(Journal)
    year = orm.Required(int)


class Borrowing(db_sql.Entity, metaclass=EntityMeta):
    """Borrowing maintains the core information of the borrowing.
    A.k.a the attrs of the borrowing relationship in the ER Diagram.
    """
    bid = orm.PrimaryKey(int, auto=True)
    uid = orm.Required(int)
    rid = orm.Required(Repository)
    borrow_date = orm.Required(datetime)
    expect_date = orm.Required(datetime)
    return_date = orm.Optional(datetime)


def bind_sqlite(filename=':memory:'):
    db_sql.bind('sqlite', filename, create_db=True)
    db_sql.generate_mapping(create_tables=True)
    with orm.db_session:
        # db_sql.execute('PRAGMA synchronous = OFF')
        db_sql.execute('PRAGMA journal_mode = WAL')
