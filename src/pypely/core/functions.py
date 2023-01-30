from functools import reduce
from typing import Any, Callable, TypeVar, Tuple
from pypely._internal.function_manipulation import define_annotation, define_signature
from pypely.helpers import flatten
from pypely._types import PypelyTuple
from pypely.memory import memorizable
from pypely.memory._context import PipelineMemoryContext
from pypely.core._safe_composition import check_and_compose, _wrap_with_error_handling
from typing_extensions import Unpack, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")
Output = TypeVar("Output")


def pipeline(*funcs: Unpack[Tuple[Callable[P, Any], Unpack[Tuple[Callable, ...]], Callable[..., Output]]]) -> Callable[P, Output]:
    first, *remaining = funcs
    initial = _wrap_with_error_handling(first) #Only the second function is wrapped with error handling in check_and_compose
    _pipeline = reduce(check_and_compose, remaining, initial)

    @memorizable
    def _call(*args: P.args, **kwargs: P.kwargs) -> Output:
        with PipelineMemoryContext() as _:
            return _pipeline(*args, **kwargs)

    _call = define_annotation(_call, funcs[0], funcs[-1].__annotations__["return"])
    _call = define_signature(_call, funcs[0], funcs[-1].__annotations__["return"])

    return _call


def fork(*funcs: Callable[P, Any]) -> Callable[P, PypelyTuple]:
    @memorizable(allow_ingest=False)
    def _fork(*args: P.args, **kwargs: P.kwargs) -> PypelyTuple:
        return PypelyTuple(*(func(*args, **kwargs) for func in funcs))

    _fork = define_annotation(_fork, funcs[0], PypelyTuple)
    _fork = define_signature(_fork, funcs[0], PypelyTuple)

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


def merge(func: Callable[P, T]) -> Callable[[PypelyTuple], T]:
    @memorizable(allow_ingest=False)
    def _merge(branches: PypelyTuple) -> T:
        flat_branches = flatten(branches)
        return func(*flat_branches)

    return _merge


def identity(x: T) -> T:
    return x
