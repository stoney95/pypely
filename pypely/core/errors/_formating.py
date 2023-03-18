from __future__ import annotations

import inspect
from collections import defaultdict
from typing import Callable, Tuple, Type, Union, get_args


def format_return_type_annotation(func: Callable) -> Union[Type, Tuple[Type, ...]]:
    """I will generate a clean form of the return type.

    `typing.Tuple` will be resolved to (<type1>, [<type2>, ...])

    Args:
        func (Callable): The function from which the return type is formated

    Returns:
        str: A clean form of the return type
    """
    return_type = func.__annotations__["return"]
    if hasattr(return_type, "__origin__"):
        if return_type.__origin__ == tuple:
            return get_args(return_type)
    return return_type


def format_parameter_signature(func: Callable) -> str:
    """I create a clean representation of the function parameters.

    Args:
        func (Callable): The function which's parameters will be displayed.

    Returns:
        str: The function parameters in this form (arg1: int, arg2: str, ...)
    """
    argspec = inspect.getfullargspec(func)
    annotations: defaultdict = defaultdict(lambda: None)
    for k, v in argspec.annotations.items():
        annotations[k] = v

    def _annotate(annotation):
        if annotation is None:
            return ""
        return f": {annotation}"

    args = ", ".join([f"{x}{_annotate(annotations[x])}" for x in argspec.args])
    return f"({args})"


def func_details(func: Callable) -> str:
    """I list details of the given function.

    I will especially be used to create clear error messages.

    Args:
        func (Callable): The function for which the details are required.

    Returns:
        str: A text describing the function name and location.
    """
    return f"'{func.__name__}' from File \"{func.__code__.co_filename}\", line {func.__code__.co_firstlineno}"
