from pypely.memory._impl import get_memory, PipelineMemory
from typing import Callable, TypeVar

T = TypeVar("T")


def add_to_memory(name: str, func: Callable[..., T]) -> Callable[..., T]:
    def __inner(*args):
        result = func(*args)
        memory = get_memory()
        memory.add(name, result)

        return result
    return __inner


def use_memory(func):
    def __inner(*args):
        memory = get_memory()
        return func(*args, memory)
    return __inner


def with_memory_attribute(name, func):
        def __inner(x, memory: PipelineMemory):
            return func(x, memory.get(name))
        return use_memory(__inner)