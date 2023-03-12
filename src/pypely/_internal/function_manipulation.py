"""I enable the manipulation of a functions metadata.

By this I enable the type checking during buildtime of a pipeline.
`define_annotation` and `define_signature` are used to copy the annotation of a given function.

This is especially useful to give the created pipeline the correct type. 
Or check that the intermediate state of a created pipeline matches the next provided step typewise. 
"""

import inspect
from copy import copy
from typing import Any, Callable, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


def define_annotation(func: Callable, copy_parameters_from: Callable[P, Any], return_type: T) -> Callable[P, T]:
    """I reset the annotation of `func`.

    The parameters from `copy_parameters_from` are set as the parameters of `func`.
    The `return_type` is set as the return annotation of `func`.

    Args:
        func (Callable): The function for which the annotations are defined
        copy_parameters_from (Callable): The function from which the parameter annotation are copied
        return_type (T): The new return type of the function

    Returns:
        Callable[P, T]: The function with new annotations
    """
    annotations = copy(copy_parameters_from.__annotations__)
    annotations["return"] = return_type

    func.__annotations__ = annotations
    return func


def define_signature(func: Callable[P, T], copy_parameters_from: Callable[P, Any], return_type: T) -> Callable[P, T]:
    """I reset the signature of `func`.

    The parameters from `copy_parameters_from` are set as the parameters of `func.__signature__`.
    The `return_type` is set as the return type of `func.__signature__`.

    Args:
        func (Callable): The function for which the signature is altered
        copy_parameters_from (Callable): The function from which the signature parameters are copied
        return_type (T): The new return type of the function signature

    Returns:
        Callable[P, T]: The function with new signature
    """
    signature = inspect.Signature(
        list(inspect.signature(copy_parameters_from).parameters.values()), return_annotation=return_type
    )

    setattr(func, "__signature__", signature)
    return func

    func.__signature__ = signature
    return func
