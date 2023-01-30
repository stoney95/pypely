from pypely.memory._impl import get_memory
from pypely.memory.errors import MemoryIngestNotAllowedError, MemoryTypeDoesNotMatchError
from pypely._internal.type_matching import is_subtype, check_if_annotations_given
from pypely.core.errors._formating import func_details


from copy import deepcopy
from typing import Callable, Dict, Type, TypeVar, Optional, Union
from typing_extensions import ParamSpec
import inspect
import uuid

T = TypeVar("T")
P = ParamSpec("P")

class MemoryEntry:
    def __init__(self):
        self.id = str(uuid.uuid4())

class Memorizable:
    def __init__(self, func: Callable[P, T], allow_ingest: bool):
        self.func = func
        self.allow_ingest = allow_ingest

        self.attributes_after = []
        self.attributes_before = []
        self.attributes_set_by_memory = set()

        self.used_memory = False
        self.written_attribute = None

        self.__qualname__ = func.__qualname__
        # self.__annotations__ = func.__annotations__
        # self.__signature__ = inspect.signature(func)
        self._execute = func

    @property
    def __annotations__(self) -> Dict[str, Type]:
        return self.func.__annotations__

    @__annotations__.setter
    def __annotations__(self, val: Dict[str, Type]):
        self.func.__annotations__ = val

    @property
    def __signature__(self) -> inspect.Signature:
        return inspect.signature(self.func)

    @__signature__.setter
    def __signature__(self, val: inspect.Signature): 
        self.func.__signature__ = val

    @property
    def __name__(self):
        return self.func.__name__

    @property
    def __code__(self):
        return self.func.__code__

    @property
    def __closure__(self):
        return self.func.__closure__

    @property
    def __module__(self):
        return self.func.__module__

    @property
    def read_attributes(self):
        return self.attributes_before + self.attributes_after

    def __rshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        _attr_name = memory_attr_name
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id

        self_copy = self.__copy_for_memory_usage()
        self_copy._execute = _add_to_memory(self.func, _attr_name)
        self_copy.written_attribute = _attr_name
        return self_copy

    def __lshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        _attr_name = memory_attr_name
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id

        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()

        parameter_name, parameter_type = self.__get_next_free_parameter_from_right()
        self.__check_memory_ingest_type(_attr_name, parameter_name, parameter_type)  

        self_copy.attributes_after.append(_attr_name)
        self_copy.attributes_set_by_memory.add(parameter_name)
        return self_copy

    def __rrshift__(self, memory_attr_name: Union[str, MemoryEntry]) -> "Memorizable":
        _attr_name = memory_attr_name
        if type(memory_attr_name) == MemoryEntry:
            _attr_name = memory_attr_name.id

        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()

        parameter_name, parameter_type = self.__get_next_free_parameter_from_left()
        self.__check_memory_ingest_type(_attr_name, parameter_name, parameter_type)        

        self_copy.attributes_before.append(_attr_name)
        self_copy.attributes_set_by_memory.add(parameter_name)
        return self_copy

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        memory = get_memory()
        memory_attributes_before = [memory.get(attr) for attr in self.attributes_before]
        memory_attributes_after = [memory.get(attr) for attr in self.attributes_after]
        
        return self._execute(*memory_attributes_before, *args, *memory_attributes_after, **kwargs)

    def __check_ingest(self):
        if not self.allow_ingest:
            raise MemoryIngestNotAllowedError(f"Memory ingest is not allowed for func: {func_details(self)}")

    def __check_memory_ingest_type(self, memory_attr_name: str, parameter_name: str, parameter_type: type):
        memory_type = get_memory().get_type(memory_attr_name)
        if not is_subtype(memory_type, parameter_type):
            raise MemoryTypeDoesNotMatchError(
                f"The memory entry \"{memory_attr_name}\" could not be ingested. The function {func_details(self)} \
                expects {parameter_type} for parameter \"{parameter_name}\". The memory entry has type {memory_type}"
            )

    def __copy_for_memory_usage(self):
        self_copy = deepcopy(self)
        self_copy.used_memory = True

        return self_copy

    def __get_next_free_parameter_from_left(self) -> tuple[str, type]:
        for name in self.__signature__.parameters:
            if not name in self.attributes_set_by_memory:
                return name, self.__annotations__[name]

    def __get_next_free_parameter_from_right(self) -> tuple[str, type]:
        for name in reversed(self.__signature__.parameters):
            if not name in self.attributes_set_by_memory:
                return name, self.__annotations__[name]


def memorizable(func: Optional[Callable[P, T]]=None, allow_ingest: Optional[bool]=True) -> Union[Callable[[Callable[P, T]], Memorizable], Callable[P, T]]:
    if func is None:
        return lambda func: Memorizable(func, allow_ingest)
    else:
        return Memorizable(func, allow_ingest)


def _add_to_memory(func: Callable[P, T], name: str) -> Callable[P, T]:
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
