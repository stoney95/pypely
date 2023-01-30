from typing import Any, Union, get_args, TypeVar, get_origin
import typing
from collections.abc import Callable, Mapping, MutableMapping, Iterable
import collections
import inspect
from pypely.core.errors import InvalidParameterAnnotationError, ParameterAnnotationsMissingError, ReturnTypeAnnotationMissingError

from itertools import zip_longest


def check_if_annotations_given(func: Callable) -> None:
    """I check if the function has type annotations.

    Args:
        func (Callable): The function that should be checked.

    Raises:
        ParameterAnnotationsMissingError: if the function has parameters without type annotations.
        ReturnTypeAnnotationMissingError: if the function has no return type annotation.
    """

    def _is_parameter_annotated(param: inspect.Parameter) -> bool:
        return not param.annotation == inspect._empty

    def _is_annotation_valid(param: inspect.Parameter) -> bool:
        invalid_types = [
            inspect.Parameter.KEYWORD_ONLY, # (arg, *, keyword_only_arg)
            inspect.Parameter.VAR_POSITIONAL, # (*args)
            inspect.Parameter.VAR_KEYWORD, # (**kwargs)
        ]

        if param.kind in invalid_types:
            return False

        return True

    parameters = inspect.signature(func).parameters
    parameters_annotated = map(_is_parameter_annotated, parameters.values())
    if not all(parameters_annotated):
        raise ParameterAnnotationsMissingError(func)

    if not "return" in func.__annotations__:
        raise ReturnTypeAnnotationMissingError(func)

    for param in parameters.values():
        if not _is_annotation_valid(param):
            raise InvalidParameterAnnotationError(func, param)



def is_subtype(type1: type[Any], type2: type[Any]) -> bool:
    """I check if `type1` is a subtype of `type2`.

    Args:
        type1 (type[Any]): The potential subtype
        type2 (type[Any]): The type which should be a super-type of `type1`

    Returns:
        bool: `True` if `type1` is a subtype of `type2`.
    """
    exceptions = [(int, float)]

    if type1 == type2: return True
    if (type1, type2) in exceptions: return True

    return _do_types_match(type1, type2)


def is_optional(_type: type):
    return get_origin(_type) is Union and \
        type(None) in get_args(_type)
        

def _do_types_match(
    actual: type[typing.Any], expected: type[typing.Any]
) -> bool:
    actual = actual.__supertype__ if _is_newtype(actual) else actual
    expected = expected.__supertype__ if _is_newtype(expected) else expected
    actual = type(None) if actual is None else actual

    if expected == actual or expected == typing.Any:
        return True

    base_type = _get_base_type(expected)

    if base_type == typing.Union:
        return any(
            _do_types_match(actual, expected_candidate)
            for expected_candidate in get_args(expected)
        )

    elif base_type in (
        _SimilarTypes.Dict
        | _SimilarTypes.List
        | _SimilarTypes.Tuple
        | _SimilarTypes.Callable
    ):
        actual_args = getattr(actual, "__args__", [])
        expected_args = getattr(expected, "__args__", [])
        return all(
            _do_types_match(actual, expected)
            for actual, expected in zip_longest(
                actual_args, expected_args, fillvalue=Any
            )
        )
    
    elif type(base_type) == TypeVar:
        return _does_resolve_typevar(actual, expected)

    elif type(actual) == TypeVar:
        return _does_resolve_typevar(expected, actual)

    try:
        return issubclass(actual, expected)
    except:
        return False


class _SimilarTypes:
    Dict = {
        dict,
        collections.OrderedDict,
        collections.defaultdict,
        Mapping,
        MutableMapping,
        typing.Dict,
        typing.DefaultDict,
        typing.Mapping,
        typing.MutableMapping,
        Iterable
    }
    List = {set, list, typing.List, typing.Set, Iterable}
    Tuple = {tuple, typing.Tuple, Iterable}
    Callable = {typing.Callable, Callable}


def _get_base_type(type_: type[typing.Any]) -> type[typing.Any]:
    if hasattr(type_, "__origin__") and type_.__origin__ is not None:
        base_type: type[typing.Any] = type_.__origin__
    elif _is_newtype(type_):
        base_type = type_.__supertype__
    elif getattr(type_, "__args__", None) or getattr(type_, "__values__", None):
        base_type = type(type_)
    else:
        base_type = type_

    return base_type


def _is_newtype(type_: type[typing.Any]) -> bool:
    return hasattr(type_, "__name__") and hasattr(type_, "__supertype__")


def _does_resolve_typevar(t1: type[typing.Any], t2: type[typing.Any]) -> bool:
    """I check if a type can be used for a typevar annotated parameter.

    If the t1 can resolve t2, the type_var will be bound to t1.

    Args:
        t1 (_type_): The type of the given argument
        t2 (_type_): The type of the parameter
        func2 (Callable): The function to which t2 belongs

    Returns:
        bool: True if t1 can be used for t2
    """
    if not type(t2) == TypeVar:
        return False

    _is_subtype = True
    _is_bound = t2.__bound__ is not None
    _has_constraints = not len(t2.__constraints__) == 0

    if _is_bound:
        _is_subtype = _is_subtype and _do_types_match(t1, t2.__bound__)

    if _has_constraints:
        _is_subtype = _is_subtype and _do_types_match(t1, t2.__constraints__)

    return _is_subtype