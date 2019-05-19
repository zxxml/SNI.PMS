#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from enum import Enum
from functools import wraps

from jsonrpc.exceptions import JSONRPCDispatchException
from jsonrpc.exceptions import JSONRPCInternalError


class Status(Enum):
    success = 0x0000
    # user related error
    username_409 = 0x1000  # username is conflict
    username_400 = 0x1001  # username doesn't exists
    password_400 = 0x1002  # password doesn't match
    # sess related error
    session_400 = 0x2000  # session doesn't exists
    session_401 = 0x2001  # session is expired
    session_403 = 0x2002  # session's user is forbidden

    @property
    def error(self):
        """Convert status to related exception."""
        return JSONRPCDispatchException(self.value, self.name)


def return_error(function):
    """This wrapper converts normal exceptions to DispatchException.
    The code will be -32603, and stringify the exceptions as message.
    """
    @wraps(function)
    def _return_error(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except JSONRPCDispatchException as e:
            raise e from None
        except Exception as e:
            code = JSONRPCInternalError.CODE
            raise JSONRPCDispatchException(code, str(e))
    return _return_error
