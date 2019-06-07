#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import json
from functools import wraps

from sni import db, rpc

users = []
journals = []
articles = []


def repeat(number):
    def _repeat(func):
        @wraps(func)
        def __repeat(*args, **kwargs):
            for i in range(number):
                func(*args, **kwargs)
        return __repeat
    return _repeat


@repeat(1000)
def test_user():
    from mimesis import Person
    person = Person()
    username = person.username()
    nickname = person.username()
    # password = person.password()
    # print(username, nickname, password)
    rpc._sign_up(username, nickname, '12345678')
    session = rpc._sign_in(username, '12345678')
    users.append(rpc._get_user(session))
    rpc._sign_out(session)


def test_article():
    with open('test.json') as fp:
        data = json.load(fp)
    for x in data['journals']:
        journal = rpc._add_journal(x['name'], x['issn'],
                                   x['isbn'], x['post'],
                                   x['host'], x['addr'],
                                   x['freq'], x['lang'],
                                   x['hist'], x['used'])
        for y in x['subscribe']:
            subscribe = rpc._add_subscribe(y['year'], journal)
            for z in y['storage']:
                storage = rpc._add_storage(z['volume'], z['number'], subscribe)
                for a in z['articles']:
                    article = rpc._add_article(a['title'], a['author'], a['pagenum'], storage, a['keyword1'],
                                               a['keyword2'], a['keyword3'], a['keyword4'], a['keyword5'])


if __name__ == '__main__':
    db.bind_sqlite()
    test_article()
