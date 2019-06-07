#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from jsonrpc import Dispatcher
from pony import orm

from sni import db, utils
from sni.utils import Fault

__all__ = ['d']
d = Dispatcher()

check_issn = utils.check_regex(r'^\d{4}-\d{4}$')
check_isbn = utils.check_regex(r'^CN\d{2}-\d{4}$')
check_post = utils.check_regex(r'^\d{1,2}-\d{1,3}$')


@d.add_method
@utils.catch_error
def restart_world():
    return _restart_world()


def _restart_world():
    """Drop all tables and recreate them."""
    db.db.drop_all_tables(with_all_data=True)
    db.db.create_tables(check_tables=True)
    _admin_sign_up('A00000000', 'Admin', '12345678')
    _guest_sign_up('G00000000', 'Guest', '12345678')


@d.add_method
@utils.catch_error
def admin_sign_up(*args, **kwargs):
    return _admin_sign_up(*args, **kwargs)


@orm.db_session
def _admin_sign_up(username,
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
def guest_sign_up(*args, **kwargs):
    return _guest_sign_up(*args, **kwargs)


@orm.db_session
def _guest_sign_up(username,
                   nickname,
                   password,
                   forename=None,
                   lastname=None,
                   mailaddr=None,
                   phonenum=None):
    password = utils.hash_pw(password)
    user = db.Guest.new(**locals())
    session = utils.new_session(user)
    return session.sessionid


@d.add_method
@utils.catch_error
def sign_up(*args, **kwargs):
    return _sign_up(*args, **kwargs)


@orm.db_session
def _sign_up(username,
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
def sign_in(*args, **kwargs):
    return _sign_in(*args, **kwargs)


@orm.db_session
def _sign_in(username, password):
    try:
        assert db.User.exists(username=username)
        user = db.User.get(username=username)
        assert utils.check_pw(password, user.password)
        session = utils.update_session(user)
        return session.sessionid
    except AssertionError:
        message = 'Login failed.'
        raise Fault(401, message)


@d.add_method
@utils.catch_error
def sign_out(*args, **kwargs):
    return _sign_out(*args, **kwargs)


@orm.db_session
@utils.check_session
def _sign_out(session):
    session = db.Session.get(sessionid=session)
    session.shelflife = utils.new_shelflife(0)


@d.add_method
@utils.catch_error
def get_user(*args, **kwargs):
    return _get_user(*args, **kwargs)


@orm.db_session
@utils.check_session
def _get_user(session):
    session = db.Session.get(sessionid=session)
    return session.user.to_dict()


@d.add_method
@utils.catch_error
@utils.check_user
def get_user_advanced(*args, **kwargs):
    return _get_user_advanced(*args, **kwargs)


@orm.db_session
def _get_user_advanced(id=None,
                       username=None,
                       nickname=None,
                       forename=None,
                       lastname=None,
                       mailaddr=None,
                       phonenum=None):
    users = db.User.select(**locals())
    users = [x.to_dict() for x in users]
    for x in users: x['password'] = str()
    return users


@d.add_method
@utils.catch_error
def set_user(*args, **kwargs):
    return _set_user(*args, **kwargs)


@orm.db_session
@utils.check_session
def _set_user(session,
              nickname=None,
              password=None,
              forename=None,
              lastname=None,
              mailaddr=None,
              phonenum=None):
    session = db.Session.get(sessionid=session)
    if isinstance(session.user, db.Guest): return
    password = password and utils.hash_pw(password)
    session.user.set(**locals())


@d.add_method
@utils.catch_error
def del_user(*args, **kwargs):
    return _del_user(*args, **kwargs)


@orm.db_session
@utils.check_session
def _del_user(session):
    session = db.Session.get(sessionid=session)
    session.user.delete()


@d.add_method
@utils.catch_error
@utils.check_admin
def add_journal(*args, **kwargs):
    return _add_journal(*args, **kwargs)


@orm.db_session
def _add_journal(name, issn,
                 isbn, post,
                 host, addr,
                 freq, lang,
                 hist=None,
                 used=None):
    try:
        assert check_issn(issn), 'ISSN'
        assert check_isbn(isbn), 'ISBN'
        assert check_post(post), 'POST'
        return db.Journal.new(**locals()).id
    except AssertionError as e:
        message = 'Invalid format: {0}.'
        raise Fault(400, message, e.args)


@d.add_method
@utils.catch_error
@utils.check_user
def get_journal(*args, **kwargs):
    return _get_journal(*args, **kwargs)


@orm.db_session
def _get_journal(id=None,
                 name=None, issn=None,
                 isbn=None, post=None,
                 host=None, addr=None,
                 freq=None, lang=None,
                 hist=None, used=None):
    journals = db.Journal.select(**locals())
    return [x.to_dict() for x in journals]


@d.add_method
@utils.catch_error
@utils.check_user
def get_journal_advanced(id=None,
                         name=None, issn=None,
                         isbn=None, post=None,
                         host=None, addr=None,
                         freq=None, lang=None,
                         hist=None, used=None):
    return _get_journal_advanced(**locals())


@orm.db_session
def _get_journal_advanced(name=None,
                          addr=None,
                          used=None,
                          **kwargs):
    journals = db.Journal.select_db(**kwargs)
    if name: journals = journals.filter(lambda x: name in x.name)
    if addr: journals = journals.filter(lambda x: addr in x.addr)
    if used: journals = journals.filter(lambda x: used in x.used)
    return [x.to_dict() for x in list(journals)]


@d.add_method
@utils.catch_error
@utils.check_user
def get_journal_reverse(*args, **kwargs):
    return _get_journal_reverse(*args, **kwargs)


@orm.db_session
def _get_journal_reverse(subscribe=None, storage=None, borrow=None):
    if subscribe is not None:
        subscribe = db.Subscribe[subscribe]
        return subscribe.journal.to_dict()
    if storage is not None:
        id = db.Storage[storage].subscribe.id
        return _get_journal_reverse(subscribe=id)
    if borrow is not None:
        id = db.Borrow[borrow].storage.id
        return _get_journal_reverse(storage=id)
    raise Fault(400, 'Condition required.')


@d.add_method
@utils.catch_error
@utils.check_admin
def set_journal(*args, **kwargs):
    return _set_journal(*args, **kwargs)


@orm.db_session
def _set_journal(id,
                 name=None, issn=None,
                 isbn=None, post=None,
                 host=None, addr=None,
                 freq=None, lang=None,
                 hist=None, used=None):
    try:
        assert issn is None or check_issn(issn), 'ISSN'
        assert isbn is None or check_isbn(isbn), 'ISBN'
        assert post is None or check_post(post), 'POST'
        db.Journal[id].set(**locals())
    except AssertionError as e:
        message = 'Invalid format: {0}.'
        raise Fault(400, message, e.args)


@d.add_method
@utils.catch_error
@utils.check_admin
def del_journal(*args, **kwargs):
    return _del_journal(*args, **kwargs)


@orm.db_session
def _del_journal(id):
    db.Journal[id].delete()


@d.add_method
@utils.catch_error
@utils.check_admin
def add_subscribe(*args, **kwargs):
    return _add_subscribe(*args, **kwargs)


@orm.db_session
def _add_subscribe(year, journal):
    journal = journal and db.Journal[journal]
    return db.Subscribe.new(**locals()).id


@d.add_method
@utils.catch_error
@utils.check_user
def get_subscribe(*args, **kwargs):
    return _get_subscribe(*args, **kwargs)


@orm.db_session
def _get_subscribe(id=None,
                   year=None,
                   journal=None):
    journal = journal and db.Journal[journal]
    subscribe = db.Subscribe.select(**locals())
    return [x.to_dict() for x in subscribe]


@d.add_method
@utils.catch_error
@utils.check_user
def get_subscribe_full(*args, **kwargs):
    return _get_subscribe_full(*args, **kwargs)


@orm.db_session
def _get_subscribe_full(id=None,
                        year=None,
                        journal=None):
    results = _get_subscribe(id=id, year=year, journal=journal)
    for x in results: x['journal'] = _get_journal(x['journal'])[0]
    return results


@d.add_method
@utils.catch_error
@utils.check_admin
def set_subscribe(*args, **kwargs):
    return _set_subscribe(*args, **kwargs)


@orm.db_session
def _set_subscribe(id,
                   year=None,
                   journal=None):
    journal = journal and db.Journal[journal]
    db.Subscribe[id].set(**locals())


@d.add_method
@utils.catch_error
@utils.check_admin
def del_subscribe(*args, **kwargs):
    return _del_subscribe(*args, **kwargs)


@orm.db_session
def _del_subscribe(id):
    db.Subscribe[id].delete()


@d.add_method
@utils.catch_error
@utils.check_admin
def add_storage(*args, **kwargs):
    return _add_storage(*args, **kwargs)


@orm.db_session
def _add_storage(volume,
                 number,
                 subscribe):
    subscribe = db.Subscribe[subscribe]
    return db.Storage.new(**locals()).id


@d.add_method
@utils.catch_error
@utils.check_user
def get_storage(*args, **kwargs):
    return _get_storage(*args, **kwargs)


@orm.db_session
def _get_storage(id=None,
                 volume=None,
                 number=None,
                 subscribe=None):
    subscribe = db.Subscribe[subscribe]
    storage = db.Storage.select(**locals())
    return [x.to_dict() for x in storage]


@d.add_method
@utils.catch_error
@utils.check_user
def get_storage_full(*args, **kwargs):
    return _get_storage_full(*args, **kwargs)


@orm.db_session
def _get_storage_full(id=None,
                      volume=None,
                      number=None,
                      subscribe=None):
    results = _get_storage(id=id, volume=volume, number=number, subscribe=subscribe)
    for x in results: x['subscribe'] = _get_subscribe_full(x['subscribe'])[0]
    return results


@d.add_method
@utils.catch_error
@utils.check_user
def is_borrowed(*args, **kwargs):
    return _is_borrowed(*args, **kwargs)


@orm.db_session
def _is_borrowed(id):
    # a storage is borrowed means borrowed and not returned
    return db.Borrow.exists_db(storage=id, returntime=None)


@d.add_method
@utils.catch_error
@utils.check_admin
def set_storage(*args, **kwargs):
    return _set_storage(*args, **kwargs)


@orm.db_session
def _set_storage(id,
                 volume=None,
                 number=None,
                 subscribe=None):
    subscribe = db.Subscribe[subscribe]
    db.Storage[id].set(**locals())


@d.add_method
@utils.catch_error
@utils.check_admin
def del_storage(*args, **kwargs):
    return _del_storage(*args, **kwargs)


@orm.db_session
def _del_storage(id):
    db.Storage[id].delete()


@d.add_method
@utils.catch_error
@utils.check_admin
def add_article(*args, **kwargs):
    return _add_article(*args, **kwargs)


@orm.db_session
def _add_article(title,
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
@utils.check_user
def get_article(*args, **kwargs):
    return _get_article(*args, **kwargs)


@orm.db_session
def _get_article(id=None,
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
@utils.check_user
def get_article_advanced(id=None,
                         title=None,
                         author=None,
                         pagenum=None,
                         storage=None,
                         keywords=None):
    return _get_article_advanced(**locals())


@orm.db_session
def _get_article_advanced(title=None,
                          author=None,
                          keywords=None,
                          **kwargs):
    results = db.Article.select_db(**kwargs)
    if title: results = results.filter(lambda x: title in x.title)
    if author: results = results.filter(lambda x: author in x.author)
    keywords = keywords.split() if keywords is not None else tuple()
    for k in keywords: results = results.filter(lambda x: k in x.keywords)
    return [x.to_dict() for x in list(results)]


@d.add_method
@utils.catch_error
@utils.check_admin
def set_article(*args, **kwargs):
    return _set_article(*args, **kwargs)


@orm.db_session
def _set_article(id,
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
@utils.check_admin
def del_article(*args, **kwargs):
    return _del_article(*args, **kwargs)


@orm.db_session
def _del_article(id):
    db.Article[id].delete()


@d.add_method
@utils.catch_error
@utils.check_admin
def add_borrow(*args, **kwargs):
    return _add_borrow(*args, **kwargs)


@orm.db_session
def _add_borrow(user,
                storage,
                borrowtime=None,
                agreedtime=None,
                returntime=None):
    try:
        assert not _is_borrowed(storage)
        user = db.User[user]
        storage = db.Storage[storage]
        borrowtime = utils.new_borrowtime(borrowtime)
        agreedtime = utils.new_agreedtime(agreedtime)
        returntime = utils.new_returntime(returntime)
        return db.Borrow.new(**locals()).id
    except AssertionError:
        message = 'Already borrowed.'
        raise Fault(409, message)


@d.add_method
@utils.catch_error
@utils.check_user
def get_borrow(*args, **kwargs):
    return _get_borrow(*args, **kwargs)


@orm.db_session
def _get_borrow(id=None,
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
@utils.check_user
def get_borrow_full(*args, **kwargs):
    return _get_borrow_full(*args, **kwargs)


@orm.db_session
def _get_borrow_full(id=None,
                     user=None,
                     storage=None,
                     borrowtime=None,
                     agreedtime=None,
                     returntime=None):
    results = _get_borrow(**locals())
    for x in results: x['user'] = _get_user_advanced(x['user'])[0]
    for x in results: x['storage'] = _get_storage_full(x['storage'])[0]
    return results


@d.add_method
@utils.catch_error
@utils.check_admin
def set_borrow(*args, **kwargs):
    return _set_borrow(*args, **kwargs)


@orm.db_session
def _set_borrow(id=None,
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
@utils.check_admin
def end_borrow(*args, **kwargs):
    return _end_borrow(*args, **kwargs)


@orm.db_session
def _end_borrow(id):
    returntime = utils.new_borrowtime()
    db.Borrow[id].set(**locals())


@d.add_method
@utils.catch_error
@utils.check_admin
def del_borrow(*args, **kwargs):
    return _del_borrow(*args, **kwargs)


@orm.db_session
def _del_borrow():
    db.Borrow[id].delete()
