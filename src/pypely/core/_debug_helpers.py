from __future__ import annotations
from ast import Call
from collections import namedtuple
import copy
from functools import wraps
from typing import Callable, TypeVar
import inspect
from typing_extensions import ParamSpec

from pypely.core.errors import PipelineCallError, PipelineForwardError, PipelineStepError, ParameterAnnotationsMissingError, ReturnTypeAnnotationMissingError, OutputInputDoNotMatchError
from pypely._types import PypelyError

DebugMemory = namedtuple('DebugMemory', ['combine', 'first', 'last'])
ExceptionSubstitution = namedtuple('ExceptionSubstitution', ['exception', 'pypely_error'])

T = TypeVar("T")
P = ParamSpec("P")
CombineFirstOutput = TypeVar("CombineFirstOutput")
CombineSecondOutput = TypeVar("CombineSecondOutput")

def debugable_combine(func1: Callable[P, CombineFirstOutput], func2: Callable[[CombineFirstOutput], CombineSecondOutput]) -> Callable[P, CombineSecondOutput]:
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

    def _combine(*args):
        return func2(func1(*args))

    _combine.__annotations__ = copy.copy(func1.__annotations__)
    _combine.__annotations__["return"] = func2.__annotations__["return"]

    return _combine


def _check_if_annotations_given(func: Callable) -> None:
    """I check if the function has type annotations.

    Args:
        func (Callable): The function that should be checked.

    Raises:
        ParameterAnnotationsMissingError: Will be raised when the function has parameters without type annotations.
        ReturnTypeAnnotationMissingError: Will be raised when the function has no return type annotation.
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
    _is_equal_type = lambda t1, t2: t1 == t2

    return_type = func1.__annotations__["return"]
    expected_parameters = copy.copy(func2.__annotations__)
    expected_parameters.pop("return")

    if return_type.__origin__ == tuple:
        return_types = return_type.__args__
    else:
        return_types = (return_type,)

    if not _is_same_length(return_types, expected_parameters):
        raise OutputInputDoNotMatchError(func1, func2)

    types_equal = [_is_equal_type(t1, t2) for (t1, t2) in zip(return_types, expected_parameters.values())]
    if not all(types_equal):
        raise OutputInputDoNotMatchError(func1, func2)


def _wrap_with_error_handling(func: Callable[..., T]) -> Callable[..., T]:
    """I provide readable error messages if something goes wrong inside a user provided function.

    Args:
        func (Callable): The user provided function

    Returns:
        Callable: The wrapped version of the user provided function
    """
    def wrap(*args) -> T:
        try:
            return func(*args)
        except Exception as e:
            if isinstance(e, PypelyError):
                raise e
            raise PipelineStepError(func, e)
    wrap.__annotations__ = func.__annotations__
    wrap.__signature__ = inspect.signature(func)
    return wrap



def _try(func: Callable, debug_memory: DebugMemory, type_error_handler):
    def wrap(*args):
        try:
            return func(*args)
        except TypeError:
            raise type_error_handler(debug_memory, func, args)
        except Exception as e:
            if isinstance(e, PypelyError):
                raise e
            raise PipelineStepError(debug_memory, func, args)

    return wrap
