#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import OrderedDict
from functools import wraps
from json import JSONDecoder

import coverage


def ignore_error(func):
    @wraps(func)
    def _ignore_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(type(e), str(e.args))
    return _ignore_error


def show_coverage(func):
    cov = coverage.Coverage()
    @wraps(func)
    def _show_coverage(*args, **kwargs):
        cov.start()
        func(*args, **kwargs)
        cov.stop()
        cov.report()
    return _show_coverage


def load_ordered(filename):
    decoder = JSONDecoder(object_pairs_hook=OrderedDict)
    return decoder.decode(open(filename).read())
