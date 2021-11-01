from functools import reduce
from typing import Callable, Tuple, TypeVar
from pypely.helpers import flatten
from pypely._types import PypelyTuple
from pypely.memory._context import PipelineMemoryContext

T = TypeVar("T")

def pipeline(*funcs: Callable) -> Callable:
    def _reducer(func1, func2):
        return lambda *x: func2(func1(*x))

    _pipeline = reduce(_reducer, funcs)

    def _call(*args):
        with PipelineMemoryContext() as _:
            return _pipeline(*args)

    return _call

def fork(*funcs: Callable) -> Callable[..., PypelyTuple]:
    return lambda *x: PypelyTuple(*[func(*x) for func in funcs])


def to(obj: T, *set_fields: str) -> Callable[[PypelyTuple], T]:
    def _inner(vals: PypelyTuple) -> T:
        vals_flattened = flatten(vals)
        if not set_fields == ():
            assert len(vals_flattened) == len(set_fields)
            fields_named = {field_name: val for field_name, val in zip(set_fields, vals_flattened)}
            return obj(**fields_named)
        else:
            return obj(*vals_flattened)
    
    return _inner


def merge(func: Callable[..., T]) -> Callable[[PypelyTuple], T]:
    return lambda branches: func(*flatten(branches))


def identity(*x):
    if len(x) == 1:
        return x[0]
    return x
