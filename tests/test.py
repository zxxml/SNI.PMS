#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from sni import db, rpc
from tests import utils

sign_up = utils.ignore_error(rpc._sign_up)
sign_in = utils.ignore_error(rpc._sign_in)
sign_out = utils.ignore_error(rpc._sign_out)

add_journal = utils.ignore_error(rpc._add_journal)
add_subscribe = utils.ignore_error(rpc._add_subscribe)
add_storage = utils.ignore_error(rpc._add_storage)
add_article = utils.ignore_error(rpc._add_article)
add_borrow = utils.ignore_error(rpc._add_borrow)

get_user = utils.ignore_error(rpc._get_user)
get_journal = utils.ignore_error(rpc._get_journal)
get_subscribe = utils.ignore_error(rpc._get_subscribe)
get_storage = utils.ignore_error(rpc._get_storage)
get_article = utils.ignore_error(rpc._get_article)
get_borrow = utils.ignore_error(rpc._get_borrow)

get_user_advanced = utils.ignore_error(rpc._get_user_advanced)
get_subscribe_full = utils.ignore_error(rpc._get_subscribe_full)
get_storage_full = utils.ignore_error(rpc._get_storage_full)
get_article_adv = utils.ignore_error(rpc._get_article_advanced)
get_borrow_full = utils.ignore_error(rpc._get_borrow_full)

set_user = utils.ignore_error(rpc._set_user)
set_journal = utils.ignore_error(rpc._set_journal)
set_subscribe = utils.ignore_error(rpc._set_subscribe)
set_storage = utils.ignore_error(rpc._set_storage)
set_article = utils.ignore_error(rpc._set_article)
set_borrow = utils.ignore_error(rpc._set_borrow)
end_borrow = utils.ignore_error(rpc._end_borrow)


def test_journals(filename):
    data = utils.load_ordered(filename)
    journals_data = data['journals']
    for x in journals_data:
        y = x.pop('subscribe')
        id = add_journal(**x)
        print(get_journal(id))
        set_journal(id, **x)
        test_subscribe(y, id)


def test_subscribe(subscribe, journal):
    for x in subscribe:
        storage = x.pop('storage')
        x['journal'] = journal
        id = add_subscribe(**x)
        print(get_subscribe(id))
        get_subscribe_full(id)
        set_subscribe(id, **x)
        test_storage(storage, id)


def test_storage(storage, subscribe):
    for x in storage:
        articles = x.pop('articles')
        x['subscribe'] = subscribe
        id = add_storage(**x)
        print(get_storage(id))
        set_storage(id, **x)
        test_articles(articles, id)


def test_articles(articles, storage):
    for x in articles:
        x['storage'] = storage
        id = add_article(**x)
        print(get_article(id))
        get_article_adv(id=id)


def test_readers():
    sign_up('R00000000', 'Reader', '12345678')
    session = sign_in('R00000000', '12345678')
    print(get_user_advanced(username='R00000000'))
    set_user(session, mailaddr='reader@sni.pms.cn')
    get_user(session)
    sign_out(session)


def test_borrow():
    id = add_borrow(1, 1)
    print(get_borrow(id))
    get_borrow_full(id)
    set_borrow(id)
    end_borrow(id)


def test_main():
    db.bind_sqlite('../sni.db')
    test_journals('test.json')
    test_readers()
    test_borrow()


if __name__ == '__main__':
    test_main()
