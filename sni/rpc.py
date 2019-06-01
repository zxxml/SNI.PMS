#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from jsonrpc import Dispatcher
from jsonrpc.exceptions import JSONRPCDispatchException as Fault
from pony import orm

from sni import db, utils

__all__ = ['d']
d = Dispatcher()

check_issn = utils.check_regex(r'^\d{4}-\d{4}$')
check_isbn = utils.check_regex(r'^CN\d{2}-\d{4}$')
check_post = utils.check_regex(r'^\d{1,2}-\d{1,3}$')


@d.add_method
@utils.catch_error
def restart_world():
    """Drop all tables and recreate them."""
    db.db.drop_all_tables(with_all_data=True)
    db.db.create_tables(check_tables=True)


@d.add_method
@utils.catch_error
@orm.db_session
def admin_sign_up(username,
                  nickname,
                  password,
                  forename=None,
                  lastname=None,
                  mailaddr=None,
                  phonenum=None):
    password = utils.hash_pw(password)
    user = db.Admin.new(**locals())
    session = utils.new_session(user)
    return session.sessionid


@d.add_method
@utils.catch_error
@orm.db_session
def sign_up(username,
            nickname,
            password,
            forename=None,
            lastname=None,
            mailaddr=None,
            phonenum=None):
    password = utils.hash_pw(password)
    user = db.Reader.new(**locals())
    session = utils.new_session(user)
    return session.sessionid


@d.add_method
@utils.catch_error
@orm.db_session
def sign_in(username, password):
    try:
        assert db.User.exists(username=username)
        user = db.User.get(username=username)
        assert utils.check_pw(password, user.password)
        session = utils.update_session(user)
        return session.sessionid
    except AssertionError:
        text = 'Wrong Password.'
        raise Fault(400, text)


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_session
def sign_out(session):
    session = db.Session.get(sessionid=session)
    session.shelflife = utils.new_shelflife(0)


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_session
def get_user(session):
    session = db.Session.get(sessionid=session)
    return session.user.to_dict()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_session
def set_user(session,
             nickname=None,
             password=None,
             forename=None,
             lastname=None,
             mailaddr=None,
             phonenum=None):
    session = db.Session.get(sessionid=session)
    password = password and utils.hash_pw(password)
    session.user.set(**locals())


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_session
def del_user(session):
    session = db.Session.get(sessionid=session)
    session.user.delete()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def add_journal(name, issn,
                isbn, post,
                host, addr,
                freq, lang,
                hist=None,
                used=None):
    try:
        assert check_issn(issn)
        assert check_isbn(isbn)
        assert check_post(post)
        return db.Journal.new(**locals()).id
    except AssertionError:
        text = 'Invalid Format.'
        raise Fault(400, text)


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_journal(id=None,
                name=None, issn=None,
                isbn=None, post=None,
                host=None, addr=None,
                freq=None, lang=None,
                hist=None, used=None):
    journals = db.Journal.select(**locals())
    return [x.to_dict() for x in journals]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def set_journal(id,
                name=None, issn=None,
                isbn=None, post=None,
                host=None, addr=None,
                freq=None, lang=None,
                hist=None, used=None):
    try:
        assert issn is None or check_issn(issn)
        assert isbn is None or check_isbn(isbn)
        assert post is None or check_post(post)
        db.Journal[id].set(**locals())
    except AssertionError:
        text = 'Invalid Format.'
        raise Fault(400, text)


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def del_journal(id):
    db.Journal[id].delete()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def add_subscribe(year, journal):
    journal = journal and db.Journal[journal]
    return db.Subscribe.new(**locals()).id


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_subscribe(id=None,
                  year=None,
                  journal=None):
    journal = journal and db.Journal[journal]
    subscribe = db.Subscribe.select(**locals())
    return [x.to_dict() for x in subscribe]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def set_subscribe(id,
                  year=None,
                  journal=None):
    journal = journal and db.Journal[journal]
    db.Subscribe[id].set(**locals())


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def del_subscribe(id):
    db.Subscribe[id].delete()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def add_storage(volume,
                number,
                subscribe):
    subscribe = db.Subscribe[subscribe]
    return db.Storage.new(**locals()).id


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_storage(id=None,
                volume=None,
                number=None,
                subscribe=None):
    subscribe = db.Subscribe[subscribe]
    storage = db.Storage.select(**locals())
    return [x.to_dict() for x in storage]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def set_storage(id,
                volume=None,
                number=None,
                subscribe=None):
    subscribe = db.Subscribe[subscribe]
    db.Storage[id].set(**locals())


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def del_storage(id):
    db.Storage[id].delete()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def add_article(title,
                author,
                pagenum,
                storage,
                keyword1=None,
                keyword2=None,
                keyword3=None,
                keyword4=None,
                keyword5=None):
    storage = db.Storage[storage]
    return db.Article.new(**locals()).id


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_article(id=None,
                title=None,
                author=None,
                pagenum=None,
                storage=None,
                keyword1=None,
                keyword2=None,
                keyword3=None,
                keyword4=None,
                keyword5=None):
    storage = storage and db.Storage[storage]
    articles = db.Article.select(**locals())
    return [x.to_dict() for x in articles]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_article_advanced(id=None,
                         title=None,
                         author=None,
                         pagenum=None,
                         storage=None,
                         keywords=None):
    kwargs = {'id': id, 'title': title, 'author': author, 'pagenum': pagenum, 'storage': db.Storage[storage]}
    result = db.Article.select().filter(**kwargs).filter(lambda x: x.keywords & set(keywords.split(' ')))
    return [x.to_dict() for x in result]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def set_article(id,
                title=None,
                author=None,
                pagenum=None,
                storage=None,
                keyword1=None,
                keyword2=None,
                keyword3=None,
                keyword4=None,
                keyword5=None):
    storage = db.Storage[storage]
    db.Article[id].set(**locals())


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def del_article(id):
    db.Article[id].delete()


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def add_borrow(user,
               storage,
               borrowtime=None,
               agreedtime=None,
               returntime=None):
    user = db.User[user]
    storage = db.Storage[storage]
    borrowtime = utils.new_borrowtime(borrowtime)
    agreedtime = utils.new_agreedtime(agreedtime)
    returntime = utils.new_returntime(returntime)
    return db.Borrow.new(**locals()).id


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_user
def get_borrow(id=None,
               user=None,
               storage=None,
               borrowtime=None,
               agreedtime=None,
               returntime=None):
    user = db.User[user]
    storage = db.Storage[storage]
    borrows = db.Borrow.select(**locals())
    return [x.to_dict() for x in borrows]


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def set_borrow(id=None,
               user=None,
               storage=None,
               borrowtime=None,
               agreedtime=None,
               returntime=None):
    user = db.User[user]
    storage = db.Storage[storage]
    borrowtime = utils.new_borrowtime(borrowtime)
    agreedtime = utils.new_agreedtime(agreedtime)
    returntime = utils.new_returntime(returntime)
    db.Borrow[id].set(**locals())


@d.add_method
@utils.catch_error
@orm.db_session
@utils.check_admin
def del_borrow():
    db.Borrow[id].delete()
