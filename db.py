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
    userId   = orm.PrimaryKey(int, auto=True) # 用户 ID
    sessId   = orm.Required(str, unique=True) # 会话 ID
    expire   = orm.Required(datetime)         # 过期时间
    username = orm.Required(str, unique=True) # 用户名
    nickname = orm.Required(str)              # 昵称
    password = orm.Required(str)              # 密码
    foreName = orm.Optional(str)              # 名字
    lastName = orm.Optional(str)              # 姓氏
    mailAddr = orm.Optional(str)              # 邮箱
    phoneNum = orm.Optional(str)              # 手机号
class Admin(User): pass  # 扩展的管理员表
class Reader(User): pass # 扩展的读者表
# ///////////////////////
# /// endregion: User ///
# ///////////////////////


# ///////////////////////
# /// region: Journal ///
# ///////////////////////
class Journal(db.Entity, metaclass=EntityMeta):
    jourId  = orm.PrimaryKey(int, auto=True) # 期刊 ID
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
    subsId = orm.PrimaryKey(int, auto=True) # 征订 ID
    jourId = orm.Required(int)              # 期刊 ID
    year   = orm.Required(int)              # 征订年份
    orm.composite_key(jourId, year)
# ///////////////////////
# /// endregion: Subs ///
# ///////////////////////


# ///////////////////////
# /// region: Storage ///
# ///////////////////////
class Storage(db.Entity, metaclass=EntityMeta):
    stoId  = orm.PrimaryKey(int, auto=True) # 库存 ID
    subsId = orm.Required(int)              # 征订 ID
    volume = orm.Required(int)              # 卷
    issue  = orm.Required(int)              # 期
# //////////////////////////
# /// endregion: Storage ///
# //////////////////////////


# ///////////////////////
# /// region: Article ///
# ///////////////////////
class Article(db.Entity, metaclass=EntityMeta):
    artId    = orm.PrimaryKey(int, auto=True) # 文章 ID
    stoId    = orm.Required(int)              # 库存 ID
    title    = orm.Required(str)              # 标题
    author   = orm.Required(str)              # 作者
    content  = orm.Required(str)              # 内容
    pageNum  = orm.Required(int)              # 页码
    keyword1 = orm.Required(str)              # 关键字
    keyword2 = orm.Required(str)
    keyword3 = orm.Required(str)
    keyword4 = orm.Required(str)
    keyword5 = orm.Required(str)
# //////////////////////////
# /// endregion: Article ///
# //////////////////////////


# //////////////////////
# /// region: Borrow ///
# //////////////////////
class Borrow(db.Entity, metaclass=EntityMeta):
    borId      = orm.PrimaryKey(int, auto=True) # 借阅 ID
    stoId      = orm.Required(int)              # 库存 ID
    userId     = orm.Required(int)              # 用户 ID
    borrowTime = orm.Required(datetime)         # 借出时间
    agreedTime = orm.Required(datetime)         # 应还时间
    returnTime = orm.Required(datetime)         # 归还时间
# /////////////////////////
# /// endregion: Borrow ///
# /////////////////////////
