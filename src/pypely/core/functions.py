from functools import reduce
from typing import Any, Callable, TypeVar, Tuple
from pypely.helpers import flatten
from pypely._types import PypelyTuple
from pypely.memory import memorizable
from pypely.memory._context import PipelineMemoryContext
from pypely.core._safe_composition import check_and_compose, _wrap_with_error_handling
from pypely.core.errors import MergeError
from typing_extensions import Unpack, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
Output = TypeVar("Output")


def pipeline(*funcs: Unpack[Tuple[Callable[P, Any], Unpack[Tuple[Callable, ...]], Callable[..., Output]]]) -> Callable[P, Output]:
    first, *remaining = funcs
    initial = _wrap_with_error_handling(first) #Only the second function is wrapped with error handling in debugable_combine
    _pipeline = reduce(check_and_compose, remaining, initial)

    @memorizable
    def _call(*args: P.args, **kwargs: P.kwargs) -> Output:
        with PipelineMemoryContext() as _:
            return _pipeline(*args, **kwargs)
    
    # _call.__annotations__ = _pipeline.__annotations__

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
