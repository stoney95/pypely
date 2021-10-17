from functools import reduce
from typing import Callable
from .helpers import flatten


def pipeline(*funcs: Callable) -> Callable:
    def _reducer(func1, func2):
        return lambda *x: func2(func1(*x))

    return reduce(_reducer, funcs)


def fork(*funcs: Callable) -> Callable:
    return lambda *x: [func(*x) for func in funcs]


def to(obj, *set_fields):
    def _inner(*vals):
        vals_flattened = flatten(vals)
        if not set_fields == ():
            assert len(vals_flattened) == len(set_fields)
            fields_named = {field_name: val for field_name, val in zip(set_fields, vals)}
            return obj(**fields_named)
        else:
            return obj(*vals_flattened)
    
    return _inner


def merge(func: Callable) -> Callable:
    return lambda branches: func(*flatten(branches))
    # return lambda branches: reduce(lambda x, y: func(x, y), branches)


identity = lambda *x: x