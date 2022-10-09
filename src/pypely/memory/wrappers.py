from pypely.memory._impl import get_memory
from pypely.memory.errors import MemoryIngestNotAllowedError

from copy import deepcopy
from typing import Callable, TypeVar, Optional, Union

T = TypeVar("T")

class Memorizable:
    def __init__(self, func: Callable[..., T], allow_ingest: bool):
        self.func = func
        self.allow_ingest = allow_ingest

        self.attributes_after = []
        self.attributes_before = []
        self.used_memory = False
        self.written_attribute = None

        self.__qualname__ = func.__qualname__
        self.__annotations__ = func.__annotations__
        self._execute = func

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

    def __rshift__(self, other):
        # return _add_to_memory(self.func, other)
        self_copy = self.__copy_for_memory_usage()
        self_copy._execute = _add_to_memory(self.func, other)
        self_copy.written_attribute = other
        return self_copy

    def __lshift__(self, other):
        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()
        self_copy.attributes_after.append(other)
        return self_copy

    def __rrshift__(self, other):
        self.__check_ingest()
        self_copy = self.__copy_for_memory_usage()
        self_copy.attributes_before.append(other)
        return self_copy

    def __call__(self, *args):
        memory = get_memory()
        memory_attributes_before = [memory.get(attr) for attr in self.attributes_before]
        memory_attributes_after = [memory.get(attr) for attr in self.attributes_after]
        
        return self._execute(*memory_attributes_before, *args, *memory_attributes_after)

    def __check_ingest(self):
        if not self.allow_ingest:
            raise MemoryIngestNotAllowedError(f"Memory ingest is not allowed for func: {self.func.__qualname__}")

    def __copy_for_memory_usage(self):
        self_copy = deepcopy(self)
        self_copy.used_memory = True

        return self_copy


def memorizable(func: Optional[Callable[..., T]]=None, allow_ingest: Optional[bool]=True) -> Union[Callable[[Callable[..., T]], Memorizable], Callable[..., T]]:
    if func is None:
        return lambda func: Memorizable(func, allow_ingest)
    else:
        return Memorizable(func, allow_ingest)


def _add_to_memory(func: Callable[..., T], name: str) -> Callable[..., T]:
    def __inner(*args):
        result = func(*args)
        memory = get_memory()
        memory.add(name, result)

        return result
    return __inner
