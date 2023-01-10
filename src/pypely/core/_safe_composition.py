from collections import namedtuple
import copy
from functools import wraps
from itertools import zip_longest
from typing import Any, Callable, List, Tuple, Type, TypeVar, get_args
import inspect
from typing_extensions import ParamSpec
from typeguard import check_type

from pypely.core.errors import PipelineStepError, ParameterAnnotationsMissingError, ReturnTypeAnnotationMissingError, OutputInputDoNotMatchError
from pypely._types import PypelyError
from pypely._internal.type_matching import is_subtype

T = TypeVar("T")
P = ParamSpec("P")
CombineFirstOutput = TypeVar("CombineFirstOutput")
CombineSecondOutput = TypeVar("CombineSecondOutput")

def check_and_compose(func1: Callable[P, CombineFirstOutput], func2: Callable[[CombineFirstOutput], CombineSecondOutput]) -> Callable[P, CombineSecondOutput]:
    """I test if two functions can be combined and do so if they fit.

    Args:
        func1 (Callable): The first function
        func2 (Callable): The second function

    Returns:
        Callable[P, CombineSecondOutput]: A function that forwards the result of func1 to func2.
    """
    _check_if_annotations_given(func1)
    _check_if_annotations_given(func2)
    _check_if_annotations_match(func1, func2)

    func2 = _wrap_with_error_handling(func2)

    def _composition(*args: P.args, **kwargs: P.kwargs) -> CombineSecondOutput:
        return func2(func1(*args, **kwargs))

    _annotations = copy.copy(func1.__annotations__)
    _annotations["return"] = func2.__annotations__["return"]

    _signature = inspect.Signature(
        inspect.signature(func1).parameters.values(),
        return_annotation=inspect.signature(func2).return_annotation
    )

    _composition.__annotations__ = _annotations
    _composition.__signature__ = _signature
    if hasattr(func2, "_typevar_usage"):
        _composition._typevar_usage = func2._typevar_usage

    return _composition


def _check_if_annotations_given(func: Callable) -> None:
    """I check if the function has type annotations.

    Args:
        func (Callable): The function that should be checked.

    Raises:
        ParameterAnnotationsMissingError: if the function has parameters without type annotations.
        ReturnTypeAnnotationMissingError: if the function has no return type annotation.
    """

    def _is_parameter_annotated(param: inspect.Parameter) -> bool:
        return not param.annotation == inspect._empty

    parameters = inspect.signature(func).parameters
    parameters_annotated = map(_is_parameter_annotated, parameters.values())
    if not all(parameters_annotated):
        raise ParameterAnnotationsMissingError(func)

    if not "return" in func.__annotations__:
        raise ReturnTypeAnnotationMissingError(func)


def _check_if_annotations_match(func1: Callable, func2: Callable) -> None:
    """I check that the output of func1 matches the input of func2.

    Args:
        func1 (Callable): The function that produces the output
        func2 (Callable): The function that consumes the output

    Raises:
        OutputInputDoNotMatchError: Is raised if the output type defers from the input type.
    """
    _is_same_length = lambda it1, it2: len(it1) == len(it2)

    return_types, expected_parameters = _collect_types(func1, func2)

    if not _is_same_length(return_types, expected_parameters):
        raise OutputInputDoNotMatchError(func1, func2)


    for (t1, t2) in zip(return_types, expected_parameters):
        if not is_subtype(t1, t2):
            raise OutputInputDoNotMatchError(func1, func2)
        
        _track_type_var_usage(t1, t2, func2)


def _collect_types(func1: Callable, func2: Callable) -> Tuple[List[Type], List[Type]]:
    """I collect all types from the function annotations.

    This also includes to resolve type vars if they have already been used with a more specific type in the given function context.

    Args:
        func1 (Callable): The function from which the output will be used.
        func2 (Callable): The function which will use the output of `func1` as input.

    Returns:
        Tuple[List[Type], List[Type]]: (
            A list with all types that are annotated as output of `func1`,
            A list with all annotated input types of `func2`
        )
    """
    return_type = func1.__annotations__["return"]
    expected_parameters = copy.copy(func2.__annotations__)
    expected_parameters.pop("return")

    return_types = (return_type,)
    if hasattr(return_type, "__origin__"):
        if return_type.__origin__ == tuple:
            return_types = return_type.__args__

    _return_types = _resolve_type_var_usage(return_types, func1)
    return _return_types, list(expected_parameters.values())


def _resolve_type_var_usage(types: List[Type], func: Callable) -> List[Type]:
    """I check if a type var has been used in the context of the given function with a more specific type.

    If a type var has been used it is replaced by that more specific type.
    This function uses the attribute `_typevar_usage` of `func`.
    This attribute has been set by the type checking if a type var was used with a more specific type.

    Args:
        types (List[Type]): The list of identified types
        func (Callable): The function to which these types belong

    Returns:
        List[Type]: The list of types, where type vars are resolved, if possible.
    """
    resolved_types = list()
    for _type in types:
        if hasattr(_type, "__args__"):
            args = get_args(_type)
            resolved_args = _resolve_type_var_usage(args, func)
            setattr(_type, "__args__", tuple(resolved_args))

            resolved_types.append(_type)
            continue

        if not type(_type) == TypeVar:
            resolved_types.append(_type)
            continue
    
        if not hasattr(func, "_typevar_usage"):
            resolved_types.append(_type)
            continue

        if not _type.__name__ in func._typevar_usage:
            resolved_types.append(_type)
            continue

        resolved_types.append(func._typevar_usage[_type.__name__])

    return resolved_types


def _track_type_var_usage(t1: type[Any], t2: type[Any], func: Callable) -> Callable:
    """I track the usage of type vars with more specific types in the context of the given function.

    If a type var is used with a more specific type it is added to the `_typevar_usage` dict of `func`.

    Args:
        t1 (type[Any]): The potentially more specific type
        t2 (type[Any]): The potential type var
        func (Callable): The function which provides and tracks the context

    Returns:
        Callable: The function with the tracked type var usage.
    """
    t1_args = get_args(t1)
    t2_args = get_args(t2)

    if t1_args and t2_args:
        for (_t1, _t2) in zip_longest(t1_args, t2_args, fillvalue=Any):
            _track_type_var_usage(_t1, _t2, func)

    if type(t2) == TypeVar:
        if not hasattr(func, "_typevar_usage"):
            func._typevar_usage = dict()
        func._typevar_usage[t2.__name__] = t1

    return func


def _wrap_with_error_handling(func: Callable[P, T]) -> Callable[P, T]:
    """I provide readable error messages if something goes wrong inside a user provided function.

    Args:
        func (Callable): The user provided function

    Returns:
        Callable: The wrapped version of the user provided function
    """
    @wraps(func)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, PypelyError):
                raise e
            raise PipelineStepError(func, e)
    wrap.__annotations__ = func.__annotations__
    wrap.__signature__ = inspect.signature(func)
    return wrap
