"""I define the API of pypely.

`pipeline` is the core of pypely. This function lets you define pipelines from bare python functions. 
You can use `fork`, `merge`, `to` and `identity` to create more complex pipelines. 

You can find more detailed examples in the examples directory.
"""

from functools import reduce
from typing import Any, Callable, Tuple, Type, TypeVar

from typing_extensions import ParamSpec, Unpack

from pypely._internal.function_manipulation import define_annotation, define_signature
from pypely._types import PypelyTuple
from pypely.core._safe_composition import _wrap_with_error_handling, check_and_compose
from pypely.memory import memorizable
from pypely.memory._context import PipelineMemoryContext

T = TypeVar("T")
P = ParamSpec("P")
Output = TypeVar("Output")


# `Unpack` is currently not supported by mypy -> type: ignore in next line
def pipeline(*funcs: Unpack[Tuple[Callable[P, Any], Unpack[Tuple[Callable, ...]], Callable[..., Output]]]) -> Callable[P, Output]:  # type: ignore
    """I chain functions together.

    I can deal with any number of provided functions. But I need at least one function.
    Functions that are fead into me need to be typed.
    The types of the provided functions need to match.

    Example:
        ```python
        from pypely import pipeline

        def open_favourite_ide():
            ...

        def create_new_conda_environment():
            ...

        ...

        use_pypely = pipeline(
            open_favourite_ide,
            create_new_conda_environment,
            activate_environment,
            install_pypely,
            have_fun_building_pipelines
        )

        use_pypely() # -> 🥳
        ```

    Args:
        funcs (Callable): The functions that will be chained to form the pipeline.

    Returns:
        Callable[P, Output]: A callable that forwards the input `P` to the first function. The output of the first function is passed to the second function, etc.
    """
    first, *remaining = funcs
    initial = _wrap_with_error_handling(
        first
    )  # Only the second function is wrapped with error handling in check_and_compose
    _pipeline = reduce(check_and_compose, remaining, initial)

    @memorizable
    def _call(*args: P.args, **kwargs: P.kwargs) -> Output:
        with PipelineMemoryContext() as _:
            return _pipeline(*args, **kwargs)

    _call = define_annotation(_call, funcs[0], funcs[-1].__annotations__["return"])
    _call = define_signature(_call, funcs[0], funcs[-1].__annotations__["return"])

    return _call


def fork(*funcs: Callable[P, Any]) -> Callable[P, PypelyTuple]:
    """I split the output into multiple parallel branches.

    Each branch recieves the same input = the output of the function previous to `fork`.

    Args:
        funcs (Callable): The functions that consume the output of the previous function in parallel.

    Returns:
        Callable[P, PypelyTuple]: A function that provides the output of all provided functions as a tuple
    """

    @memorizable(allow_ingest=False)  # type: ignore
    def _fork(*args: P.args, **kwargs: P.kwargs) -> PypelyTuple:
        return PypelyTuple(*(func(*args, **kwargs) for func in funcs))

    _fork_annotated = define_annotation(_fork, funcs[0], _fork.__annotations__["return"])
    _fork_signed = define_signature(_fork_annotated, funcs[0], _fork.__annotations__["return"])

    return _fork_signed


def to(cls: Type[T], *set_fields: str) -> Callable[[PypelyTuple], T]:
    """I convert multiple branches into an object.

    I can only be used after fork.
    My purpose is to bring the created branches back together.
    The output of each branch will be used to instantiate the object.
    The output of the first branch will be set as the first attribute of `obj` etc.

    `set_fields` can be used to adjust the order in which the outputs are used for instantiation.
    The following example demonstrates how `to` can be used with fields to specify to order in which the outputs of `fork` are used.

    Example:
        ```python
        @dataclass
        class Table:
            tea: Tea
            plate: Plate
            bread: Bread
            eggs: Eggs


        morning_routine = pipeline(
            wake_up,
            go_to_kitchen,
            fork(
                make_tea,
                fry_eggs,
                cut_bread,
                get_plate
            ),
            to(Table, "tea", "eggs", "bread", "plate")
        )
        ```

    Args:
        cls (Type[T]): A class that will be instantiated by the outputs of the previous `fork`
        set_fields (str): This can be used to define the order in which the fields are set.
            Please check out the example for a better explanation.

    Returns:
        Callable[[PypelyTuple], T]: A function that will instantiate the object when called
    """

    @memorizable(allow_ingest=False)  # type: ignore
    def _to(vals: PypelyTuple) -> T:
        vals_flattened = _flatten(vals)
        if not set_fields == ():
            assert len(vals_flattened) == len(set_fields)
            fields_named = {field_name: val for field_name, val in zip(set_fields, vals_flattened)}
            return cls(**fields_named)
        else:
            return cls(*vals_flattened)

    def _mock_function(p: PypelyTuple) -> None:
        pass

    _to_annotated = define_annotation(_to, _mock_function, _to.__annotations__["return"])
    _to_signed = define_signature(_to_annotated, _mock_function, _to.__annotations__["return"])

    return _to_signed


def merge(func: Callable[P, T]) -> Callable[[PypelyTuple], T]:
    """I merge multiple branches.

    I can only run after `fork`. I bring multiple branches back together.
    The given function `func` will recieve all outputs of the previous `fork`.
    `func` will recieve the outputs in order.
    `func` needs to take as many arguments as there are branches

    Args:
        func (Callable[P, T]): The function that defines the logic for how the branches will be merged.

    Returns:
        Callable[[PypelyTuple], T]: A function that will apply `func` to the outputs of the previous `fork`
    """

    @memorizable(allow_ingest=False)  # type: ignore
    def _merge(branches: PypelyTuple) -> T:
        flat_branches = _flatten(branches)
        return func(*flat_branches)

    def _mock_function(p: PypelyTuple) -> None:
        pass

    _merge_annotated = define_annotation(_merge, _mock_function, _merge.__annotations__["return"])
    _merge_signed = define_signature(_merge_annotated, _mock_function, _merge.__annotations__["return"])

    return _merge_signed


def identity(x: T) -> T:
    """I forward the given input untouched.

    This can be useful if you want to forward a result for a later step.
    As this approach can also make the pipeline hard to understand, it is advised to use [pypely.memory.memorizable][]

    Args:
        x (T): Any input

    Returns:
        T: The input is unchanged.
    """
    return x


def _flatten(_tuple: PypelyTuple) -> PypelyTuple:
    """I transform nested `PypelyTuples` into a flat `PypelyTuple`.

    Args:
        _tuple (PypelyTuple): A potentially nested `PypelyTuple`

    Raises:
        ValueError: if the input is not a `PypelyTuple`

    Returns:
        PypelyTuple: the flat `PypelyTuple`
    """
    result = []
    if isinstance(_tuple, PypelyTuple):
        for elem in _tuple:
            if isinstance(elem, PypelyTuple):
                if any(isinstance(x, PypelyTuple) for x in elem):
                    result += list(_flatten(elem))
                else:
                    result += list(elem)
            else:
                result.append(elem)
        return PypelyTuple(*result)
    raise ValueError(f"You can use flatten only with 'PypelyTuple'. Input is of type: {type(_tuple)}")
