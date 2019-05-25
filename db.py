#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime

from pony import orm

db = orm.Database()
cfg = ConfigParser()
cfg.read('sni.ini')


def bind_sqlite(filename):
    db.bind('sqlite', filename, create_db=True)
    db.generate_mapping(create_tables=True)
    with orm.db_session:
        # db.execute('PRAGMA synchronous = OFF')
        db.execute('PRAGMA journal_mode = WAL')


class EntityMeta(orm.core.EntityMeta):
    @staticmethod
    def clean_kwargs(kwargs):
        return {k: kwargs[k] for k in kwargs
                if kwargs[k] is not None}

    @orm.db_session
    def new(cls, *args, **kwargs):
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
    def select(cls, **kwargs):
        kwargs = cls.clean_kwargs(kwargs)
        return super().select().filter(**kwargs)[:]


@orm.db_session
def delete_db(self, **kwargs):
    kwargs = User.clean_kwargs(kwargs)
    self.delete_db(**kwargs)


@orm.db_session
def set_db(self, **kwargs):
    kwargs = User.clean_kwargs(kwargs)
    self.set_db(**kwargs)


db.Entity.delete_db = db.Entity.delete
db.Entity.set_db = db.Entity.set
db.Entity.delete = delete_db
db.Entity.set = set_db


# ////////////////////
# /// region: User ///
# ////////////////////
class User(db.Entity, metaclass=EntityMeta):
    user_id   = orm.PrimaryKey(int, auto=True)  # 用户 ID
    sess_id   = orm.Required(str, unique=True)  # 会话 ID
    expires   = orm.Required(datetime)          # 过期时间
    username  = orm.Required(str, unique=True)  # 用户名
    nickname  = orm.Required(str)               # 昵称
    password  = orm.Required(str)               # 密码
    fore_name = orm.Optional(str)               # 名字
    last_name = orm.Optional(str)               # 姓氏
    mail_addr = orm.Optional(str)               # 邮箱
    phone_num = orm.Optional(str)               # 手机号
class Admin(User): pass  # 扩展的管理员表
class Reader(User): pass # 扩展的读者表
# ///////////////////////
# /// endregion: User ///
# ///////////////////////


# ///////////////////////
# /// region: Journal ///
# ///////////////////////
class Journal(db.Entity, metaclass=EntityMeta):
    jour_id = orm.PrimaryKey(int, auto=True) # 期刊 ID
    name    = orm.Required(str)              # 期刊名称
    lang    = orm.Required(str)              # 语种
    hist    = orm.Required(str)              # 创刊时间
    freq    = orm.Required(str)              # 出版周期
    issn    = orm.Required(str, unique=True) # ISSN 刊号
    cnc     = orm.Required(str, unique=True) # CN 刊号
    pdc     = orm.Required(str, unique=True) # 邮发代号
    used    = orm.Optional(str)              # 曾用名
    addr    = orm.Optional(str)              # 汇款地址
    org     = orm.Optional(str)              # 主办单位
    pub     = orm.Optional(str)              # 出版单位
# //////////////////////////
# /// endregion: Journal ///
# //////////////////////////


# ////////////////////
# /// region: Subs ///
# ////////////////////
class Subs(db.Entity, metaclass=EntityMeta):
    subs_id = orm.PrimaryKey(int, auto=True) # 征订 ID
    jour_id = orm.Required(int)              # 期刊 ID
    year    = orm.Required(int)              # 征订年份
    orm.composite_key(jour_id, year)
# ///////////////////////
# /// endregion: Subs ///
# ///////////////////////


class Storage(db.Entity, metaclass=EntityMeta):
    sto_id = orm.PrimaryKey(int, auto=True)
    subs_id = orm.Required(int)
    vol = orm.Required(int)
    iss = orm.Required(int)


class Article(db.Entity, metaclass=EntityMeta):
    art_id = orm.PrimaryKey(int, auto=True)
    sto_id = orm.Required(int)
    page_num = orm.Required(int)
    title = orm.Required(str)
    author = orm.Required(str)
    content = orm.Required(str)
    keyword1 = orm.Required(str)
    keyword2 = orm.Required(str)
    keyword3 = orm.Required(str)
    keyword4 = orm.Required(str)
    keyword5 = orm.Required(str)


class Borrow(db.Entity, metaclass=EntityMeta):
    bor_id = orm.PrimaryKey(int, auto=True)
    sto_id = orm.Required(int)
    user_id = orm.Required(int)
    borrow_time = orm.Required(datetime)
    agreed_time = orm.Required(datetime)
    return_time = orm.Required(datetime)
