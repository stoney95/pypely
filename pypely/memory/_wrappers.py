"""I provide a wrapper that allow a function to interact with the memory.

By wrapping a function with `memorizable` it can be combined with the shift operators (`<<`, `>>`).
This allows to read from or write to the memory.
`memorizable` is typically used as a function decorator.
"""

import inspect
import uuid
from copy import deepcopy
from typing import Callable, Dict, Generic, List, Optional, Set, Type, TypeVar, Union

from typing_extensions import ParamSpec

from pypely._internal.type_matching import check_if_annotations_given, is_subtype
from pypely.core.errors._formating import func_details
from pypely.memory._impl import get_memory
from pypely.memory.errors import MemoryIngestNotAllowedError, MemoryTypeDoesNotMatchError, NoFreeParameterFound

T = TypeVar("T")
P = ParamSpec("P")


class MemoryEntry:
    """I can be used to describe a memory entry.

    This allows to use a clear name which is internally handled as a uuid.
    In the future `memorizable` might only support me instead of using strings.
    If you run into naming conflicts use me instead of a string to reference the memory entry.

    Example:
        ```python
        from pypely import pipeline
        from pypely.memory import memorizable, MemoryEntry

        @memorizable
        def some_func() -> int:
            return 42

        intermediate_result = MemoryEntry()
        pipeline(
            ...,
            some_func >> intermediate_result
        )
        ```
    """

    id: str

    def __init__(self):
        self.id = str(uuid.uuid4())


class Memorizable(Generic[P, T]):
    """I am the wrapper that allows interaction with the memory."""

    attributes_after: List[str]
    attributes_before: List[str]
    attributes_set_by_memory: Set[str]
    written_attribute: Optional[str]

    def __init__(self, func: Callable[P, T], allow_ingest: Optional[bool]):
        self.func = func
        self.allow_ingest = True if allow_ingest is None else allow_ingest

        self.attributes_after = []
        self.attributes_before = []
        self.attributes_set_by_memory = set()

        self.used_memory = False
        self.written_attribute = None

        self.__qualname__ = func.__qualname__
        self._execute = func

    @property
    def __annotations__(self) -> Dict[str, Type]:
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.func.__annotations__

    @__annotations__.setter
    def __annotations__(self, val: Dict[str, Type]):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        self.func.__annotations__ = val

    @property
    def __signature__(self) -> inspect.Signature:
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return inspect.signature(self.func)

    @__signature__.setter
    def __signature__(self, val: inspect.Signature):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        setattr(self.func, "__signature__", val)

    @property
    def __name__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.func.__name__

    @property
    def __code__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.func.__code__

    @property
    def __module__(self):
        """noqa: D105.

        # noqa: DAR101
        # noqa: DAR201
        """
        return self.func.__module__

    def __rshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        """I am this operator: `func >> "name"`.

        I am used to write the output of `func` into the memory.
        The output is referenced as "name".

        Args:
            memory_attr_name (Union[str, MemoryEntry]): The name of the memory entry that will be ingested into the function

        Returns:
            Memorizable: a copy of the Memorizable object.
        """
        _attr_name = ""
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id
        else:
            _attr_name = str(memory_attr_name)  # str() required for mypy

        self_copy = self.__copy_for_memory_usage()
        self_copy._execute = _add_to_memory(self.func, _attr_name)
        self_copy.written_attribute = _attr_name
        return self_copy

    def __lshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        """I am this operator: `func << "name"`.

        I can be used to ingest parameters from the right side. It is also possible to ingest multiple parameters:
        `func << "in1" << "in2"`

        Args:
            memory_attr_name (Union[str, MemoryEntry]): The name of the memory entry.

        Returns:
            Memorizable: a copy of the Memorizable object.
        """
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id
        else:
            _attr_name = str(memory_attr_name)  # str() required for mypy

        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()

        parameter_name, parameter_type = self.__get_next_free_parameter_from_right()
        self.__check_memory_ingest_type(_attr_name, parameter_name, parameter_type)

        self_copy.attributes_after.append(_attr_name)
        self_copy.attributes_set_by_memory.add(parameter_name)
        return self_copy

    def __rrshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        """I am this operator: `"name" >> func`.

        I am used to ingest memory entries from the left side into the function.
        It is possible to ingest multiple objects from the left side. But this needs to be wrapped in paranthesis:
        `"in2" >> ("in1" >> func)`

        Args:
            memory_attr_name (Union[str, MemoryEntry]): _description_

        Returns:
            Memorizable: a copy of the Memorizable object.
        """
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id
        else:
            _attr_name = str(memory_attr_name)  # str() required for mypy

        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()

        parameter_name, parameter_type = self.__get_next_free_parameter_from_left()
        self.__check_memory_ingest_type(_attr_name, parameter_name, parameter_type)

        self_copy.attributes_before.append(_attr_name)
        self_copy.attributes_set_by_memory.add(parameter_name)
        return self_copy

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """I execute the function with the provided arguments and defined memory entries.

        The memory entries are loaded and combined with the given arguments.

        Args:
            args: The positional arguments given to the function
            kwargs: The keyword arguments given to the function

        Returns:
            T: the object returned by the called function.
        """
        memory = get_memory()
        memory_attributes_before = [memory.get(attr) for attr in self.attributes_before]
        memory_attributes_after = [memory.get(attr) for attr in self.attributes_after]

        return self._execute(*memory_attributes_before, *args, *memory_attributes_after, **kwargs)

    def __check_ingest(self):
        """I check if the function allows memory ingestion.

        Raises:
            MemoryIngestNotAllowedError: if the function does not allow memory ingestion.
        """
        if not self.allow_ingest:
            raise MemoryIngestNotAllowedError(f"Memory ingest is not allowed for func: {func_details(self)}")

    def __check_memory_ingest_type(self, memory_attr_name: str, parameter_name: str, parameter_type: type):
        """I check if the type of memory entry matches the type of the function parameter it will be used for.

        Args:
            memory_attr_name (str): The name of the memory entry.
            parameter_name (str): The name of the parameter the memory entry will be used for.
            parameter_type (type): The type of the parameter the memory entry will be used for.

        Raises:
            MemoryTypeDoesNotMatchError: if the type of the memory entry does not match the type of the parameter it will be used for.
        """
        memory_type = get_memory().get_type(memory_attr_name)
        if not is_subtype(memory_type, parameter_type):
            raise MemoryTypeDoesNotMatchError(
                f'The memory entry "{memory_attr_name}" could not be ingested. The function {func_details(self)} \
                expects {parameter_type} for parameter "{parameter_name}". The memory entry has type {memory_type}'
            )

    def __copy_for_memory_usage(self) -> "Memorizable":
        """I duplicate the memory wrapper.

        I am important so that multiple memory interactions of a single function work properly.
        Without me this would not be possible: `"in1" >> func << "in2" >> "out"`.

        Returns:
            Memorizable: a copy of myself.
        """
        self_copy = deepcopy(self)
        self_copy.used_memory = True

        return self_copy

    def __get_next_free_parameter_from_left(self) -> tuple[str, type]:
        """I check which parameter from the left has not been set by a call to the memory entry.

        Given a function with the following signature `example(arg1: int, arg2: int, arg3: int, arg4: int) -> int`.
        This function has already been used with memory ingestion from the left: `"memory_entry" >> example`.
        In this case `arg1` has already been set by an memory entry.
        So the next free entry from the left would be: `arg2`.

        Raises:
            NoFreeParameterFound: if all parameters have already been set by a memory entry.

        Returns:
            tuple[str, type]: the name and the type of the next free argument.
        """
        for name in self.__signature__.parameters:
            if not name in self.attributes_set_by_memory:
                return name, self.__annotations__[name]

        raise NoFreeParameterFound(
            f"Could not find a free parameter where the memory entry could be ingested. I started to search from the left side. \
            The internal function: {func_details(self)}. These attributes are already set by memory entries: {self.attributes_set_by_memory}"
        )

    def __get_next_free_parameter_from_right(self) -> tuple[str, type]:
        """I check which parameter from the right has not been set by a call to the memory entry.

        This works the same as `__get_next_free_parameter_from_left` but operates from the other side.
        A argument is set from the right side like this: `example << "memory_entry"`.

        Raises:
            NoFreeParameterFound: if all parameters have already been set by a memory entry.

        Returns:
            tuple[str, type]: the name and the type of the next free argument.
        """
        for name in reversed(self.__signature__.parameters):
            if not name in self.attributes_set_by_memory:
                return name, self.__annotations__[name]

        raise NoFreeParameterFound(
            f"Could not find a free parameter where the memory entry could be ingested. I started to search from the right side. \
            The internal function: {func_details(self)}. These attributes are already set by memory entries: {self.attributes_set_by_memory}"
        )


def memorizable(
    func: Optional[Callable[P, T]] = None, allow_ingest: Optional[bool] = True
) -> Union[Callable[[Callable[P, T]], Callable[P, T]], Callable[P, T]]:
    """I enable a function to interact with the memory.

    The `func` parameter is usually not given directly. This is done via decorators. So memorizable can be used in two ways:

    Example:
        ```python
        from pypely.memory import memorizable


        @memorizable
        def some_func_that_allows_ingest(arg1: int) -> int:
            ...


        @memorizable(allow_ingest=False)
        def some_func_that_does_not_allow_ingest(arg1: int) -> int:
            ...
        ```

    Args:
        func (Optional[Callable[P, T]], optional): The function that wants to interact with the memory. Defaults to None.
        allow_ingest (Optional[bool], optional): This describes if data from the memory can be ingested into the function. Defaults to True.

    Returns:
        Union[Callable[[Callable[P, T]], Memorizable], Callable[P, T]]: A callable that allows to use the shift operators (`<<`, `>>`)
    """
    if func is None:

        def _wrap(func: Callable[P, T]) -> Callable[P, T]:
            return Memorizable(func, allow_ingest)

        return _wrap
    else:
        return Memorizable(func, allow_ingest)


def _add_to_memory(func: Callable[P, T], name: str) -> Callable[P, T]:
    """I write the function output into the memory.

    I am used in `Memorizable` and am not meant to be used by you directly.


    Args:
        func (Callable[P, T]): The functions who's output will be written to the memory.
        name (str): The name of the memory entry.

    Returns:
        Callable[P, T]: The function wrapped with a memory interaction handler.
    """
    check_if_annotations_given(func)

    memory = get_memory()
    return_type = func.__annotations__["return"]
    memory.add_type(name, return_type)

    def __inner(*args: P.args, **kwargs: P.kwargs):
        result = func(*args, **kwargs)
        memory = get_memory()
        memory.add(name, result)

        return result

    return __inner
