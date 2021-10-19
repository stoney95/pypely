from functools import reduce
from typing import Callable, Tuple, TypeVar
from .helpers import flatten

T = TypeVar("T")

def pipeline(*funcs: Callable) -> Callable:
    def _reducer(func1, func2):
        return lambda *x: func2(func1(*x))

    return reduce(_reducer, funcs)


def fork(*funcs: Callable) -> Callable[..., Tuple]:
    return lambda *x: tuple(func(*x) for func in funcs)


def to(obj: T, *set_fields) -> Callable[..., T]:
    def _inner(*vals) -> T:
        vals_flattened = flatten(vals)
        if not set_fields == ():
            assert len(vals_flattened) == len(set_fields)
            fields_named = {field_name: val for field_name, val in zip(set_fields, vals_flattened)}
            return obj(**fields_named)
        else:
            return obj(*vals_flattened)
    
    return _inner


def merge(func: Callable[..., T]) -> Callable[[Tuple], T]:
    return lambda branches: func(*flatten(branches))


identity = lambda *x: x