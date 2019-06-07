#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import json

from sni import db
from sni.rpc import _add_article, _add_journal, _add_storage, _add_subscribe


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
