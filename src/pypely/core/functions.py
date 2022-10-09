from functools import reduce
from typing import Callable, TypeVar
from pypely.helpers import flatten
from pypely._types import PypelyTuple
from pypely.memory import memorizable
from pypely.memory._context import PipelineMemoryContext
from pypely.core._debug_helpers import debugable_reduce, DebugMemory, _wrap_with_error_handling
from pypely.core.errors import MergeError

T = TypeVar("T")


def pipeline(*funcs: Callable) -> Callable:
    initial = _wrap_with_error_handling(funcs[0])
    _pipeline = reduce(debugable_reduce, funcs[1:], initial)

    @memorizable
    def _call(*args):
        with PipelineMemoryContext() as _:
            return _pipeline(*args)
    
    _call.__annotations__ = _pipeline.__annotations__

    return _call


def fork(*funcs: Callable) -> Callable[..., PypelyTuple]:
    @memorizable(allow_ingest=False)
    def _fork(*args):
        return PypelyTuple(*[func(*args) for func in funcs])

    return _fork


def to(obj: T, *set_fields: str) -> Callable[[PypelyTuple], T]:
    @memorizable(allow_ingest=False)
    def _to(vals: PypelyTuple) -> T:
        vals_flattened = flatten(vals)
        if not set_fields == ():
            assert len(vals_flattened) == len(set_fields)
            fields_named = {field_name: val for field_name, val in zip(set_fields, vals_flattened)}
            return obj(**fields_named)
        else:
            return obj(*vals_flattened)
    
    return _to


def merge(func: Callable[..., T]) -> Callable[[PypelyTuple], T]:
    @memorizable(allow_ingest=False)
    def _merge(branches):
        flat_branches = flatten(branches)
        try:
            return func(*flat_branches)
        except TypeError:
            raise MergeError(func, branches)

    return _merge


def identity(*x):
    if len(x) == 1:
        return x[0]
    return x
