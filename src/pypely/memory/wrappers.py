from pypely.memory._impl import get_memory, PipelineMemory
from pypely.memory.errors import MemoryIngestNotAllowedError
from typing import Callable, TypeVar, Optional, Union

T = TypeVar("T")

Memorizable = Callable([Callable[..., T]], Callable[..., T])


def memorizable(func: Optional[Callable[..., T]]=None, allow_ingest: Optional[bool]=True) -> Union[Memorizable, Callable[..., T]]:
    class Memorizable:
        def __init__(self, func):
            self.func = func
            self.attributes_after = []
            self.attributes_before = []

        def __rshift__(self, other):
            return _add_to_memory(self.func, other)

        def __lshift__(self, other):
            self.__check_ingest()
            self.attributes_after.append(other)
            return self

        def __rrshift__(self, other):
            self.__check_ingest()
            self.attributes_before.append(other)
            return self

        def __call__(self, *args):
            memory = get_memory()
            memory_attributes_before = [memory.get(attr) for attr in self.attributes_before]
            memory_attributes_after = [memory.get(attr) for attr in self.attributes_after]
            return self.func(*memory_attributes_before, *args, *memory_attributes_after)

        def __check_ingest(self):
            if not allow_ingest:
                raise MemoryIngestNotAllowedError(f"Memory ingest is not allowed for func: {self.func.__qualname__}")
    
    if func is None:
        return Memorizable
    else:
        return Memorizable(func)


def _add_to_memory(func: Callable[..., T], name: str, ) -> Callable[..., T]:
    def __inner(*args):
        result = func(*args)
        memory = get_memory()
        memory.add(name, result)

        return result
    return __inner


def _use_memory(func):
    def __inner(*args):
        memory = get_memory()
        return func(*args, memory)
    return __inner


def _with_memory_attribute(func, name):
        def __inner(x, memory: PipelineMemory):
            return func(x, memory.get(name))
        return _use_memory(__inner)
