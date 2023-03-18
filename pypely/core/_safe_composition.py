import inspect
from functools import wraps
from itertools import zip_longest
from types import MappingProxyType
from typing import Any, Callable, Iterable, List, Set, Tuple, Type, TypeVar, get_args

from typing_extensions import ParamSpec

from pypely._internal.function_manipulation import define_annotation, define_signature
from pypely._internal.type_matching import check_if_annotations_given, is_optional, is_subtype
from pypely._types import PypelyError, PypelyTuple
from pypely.core.errors import OutputInputDoNotMatchError, PipelineStepError

T = TypeVar("T")
P = ParamSpec("P")
CombineFirstOutput = TypeVar("CombineFirstOutput")
CombineSecondOutput = TypeVar("CombineSecondOutput")


def check_and_compose(
    func1: Callable[P, CombineFirstOutput], func2: Callable[[CombineFirstOutput], CombineSecondOutput]
) -> Callable[P, CombineSecondOutput]:
    """I test if two functions can be combined and do so if they fit.

    Args:
        func1 (Callable): The first function
        func2 (Callable): The second function

    Returns:
        Callable[P, CombineSecondOutput]: A function that forwards the result of func1 to func2.
    """
    check_if_annotations_given(func1)
    check_if_annotations_given(func2)
    _check_if_annotations_match(func1, func2)

    func2 = _wrap_with_error_handling(func2)

    def _composition(*args: P.args, **kwargs: P.kwargs) -> CombineSecondOutput:
        _result = func1(*args, **kwargs)
        if type(_result) == tuple and type(_result) != PypelyTuple:
            return func2(*_result)

        if _result is None:
            return func2()

        return func2(_result)

    _composition = define_annotation(_composition, func1, func2.__annotations__["return"])
    _composition = define_signature(_composition, func1, func2.__annotations__["return"])

    if hasattr(func2, "_typevar_usage"):
        _typevar_usage = getattr(func2, "_typevar_usage")
        setattr(_composition, "_typevar_usage", _typevar_usage)

    return _composition


def _check_if_annotations_match(func1: Callable, func2: Callable) -> None:
    """I check that the output of func1 matches the input of func2.

    Args:
        func1 (Callable): The function that produces the output
        func2 (Callable): The function that consumes the output

    Raises:
        OutputInputDoNotMatchError: Is raised if the output type defers from the input type.
    """
    return_types, expected_parameters = _collect_types(func1, func2)
    try:
        expected_parameters = _trim_optional_expected_parameters(len(return_types), expected_parameters)
    except RuntimeError as re:
        raise OutputInputDoNotMatchError(func1, func2, re)

    for t1, t2 in zip(return_types, expected_parameters):
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
    _filter_none_annotations = lambda types: [t for t in types if t is not None]

    return_type = func1.__annotations__["return"]
    expected_parameters = inspect.signature(func2).parameters

    return_types: Tuple[Type, ...] = (return_type,)
    if hasattr(return_type, "__origin__"):
        if return_type.__origin__ == tuple:
            return_types = get_args(return_type)

    _return_types = _resolve_type_var_usage(return_types, func1)
    _return_types = _filter_none_annotations(_return_types)
    _expected_types = _resolve_memory_usage(expected_parameters, func2)
    return _return_types, _expected_types


def _trim_optional_expected_parameters(number_return_types: int, expected_parameters: list[type]) -> list[type]:
    """I trim all optional arguments so that `expected_parameters` matches the return types.

    Args:
        number_return_types (int): The number of types returned from the previous function.
        expected_parameters (list[type]): The list of all expected parameters.

    Returns:
        list[type]: The list of expected parameters that fit the number of returned types.

    Raises:
        RuntimeError: if there are more non optional `expected_parameters` than number of return types.
    """
    non_optional_types = filter(lambda t: not is_optional(t), expected_parameters)
    number_non_optional_expected_parameters = len(list(non_optional_types))
    number_all_expected_parameters = len(expected_parameters)

    if number_non_optional_expected_parameters > number_return_types:
        raise RuntimeError(
            f"Could not trim expected_parameters. There are too many non optional parameters. \
            number of return types: {number_return_types}. \
            number of non optional expected parameters: {number_non_optional_expected_parameters}"
        )

    if number_all_expected_parameters < number_return_types:
        raise RuntimeError(
            f"There are too many arguments provided. \
            number of return types: {number_return_types}. \
            number of all expected parameters: {number_all_expected_parameters}"
        )

    return expected_parameters[:number_return_types]


def _resolve_type_var_usage(types: Iterable[Type], func: Callable) -> List[Type]:
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


def _resolve_memory_usage(
    parameter_annotations: MappingProxyType[str, inspect.Parameter], func: Callable
) -> List[type]:
    """I check if the function has parameters that are filled from the memory.

    If a parameter is filled from the memory it is removed from the list of expected types.

    Args:
        parameter_annotations (MappingProxyType[str, type]): The parameter annotations of the given function.
        func (Callable): The function. If it is a `memorizable` it has stored which parameters are set by the memory.

    Returns:
        List[type]: The list of all types that are expected to be provided by the previous function.
    """
    memory_parameters: Set[str] = getattr(func, "attributes_set_by_memory", set())
    function_parameters = set(parameter_annotations.keys())
    expected_parameters = function_parameters.difference(memory_parameters)

    # It's important to keep the order. This can only be guaranteed when looping over the parameter_annotations
    expected_types = [
        parameter_annotations[name].annotation for name in parameter_annotations if name in expected_parameters
    ]
    return expected_types


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
        for _t1, _t2 in zip_longest(t1_args, t2_args, fillvalue=Any):
            _track_type_var_usage(_t1, _t2, func)  # type: ignore

    if type(t2) == TypeVar:
        if not hasattr(func, "_typevar_usage"):
            setattr(func, "_typevar_usage", dict())
        func._typevar_usage[t2.__name__] = t1  # type: ignore

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
    wrap.__signature__ = inspect.signature(func)  # type: ignore
    return wrap
