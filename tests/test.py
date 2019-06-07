#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import json
from functools import wraps

from sni import db, rpc


def ignore_error(func):
    @wraps(func)
    def _ignore_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(type(e), str(e.args))
    return _ignore_error


_add_journal = ignore_error(rpc._add_journal)
_add_subscribe = ignore_error(rpc._add_subscribe)
_add_storage = ignore_error(rpc._add_storage)
_add_article = ignore_error(rpc._add_article)


def load_from_json(content):
    data = json.loads(content)
    _load_journals(data['journals'])


def _load_journals(journals):
    for x in journals:
        y = x.pop('subscribe')
        id = _add_journal(**x)
        _load_subscribe(y, id)


def _load_subscribe(subscribe, journal):
    for x in subscribe:
        id = _add_subscribe(x['year'], journal)
        _load_storage(x['storage'], subscribe=id)


def _load_storage(storage, subscribe):
    for x in storage:
        id = _add_storage(x['volume'], x['number'], subscribe)
        for y in x['articles']: _add_article(storage=id, **y)


def test_main():
    db.bind_sqlite()
    with open('test.json') as fp:
        content = fp.read()
    load_from_json(content)


if __name__ == '__main__':
    test_main()
