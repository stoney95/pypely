from pypely.memory._impl import get_memory, PipelineMemory
from typing import Callable, TypeVar
from functools import partial

T = TypeVar("T")


class memorizable:

    def __init__(self, func):
        self.func = func
        self.attributes_after = []
        self.attributes_before = []

    def __rshift__(self, other):
        return add_to_memory(self.func, other)

    def __lshift__(self, other):
        self.attributes_after.append(other)
        return self

    def __rrshift__(self, other):
        self.attributes_before.append(other)
        return self

    def __call__(self, *args):
        memory = get_memory()
        memory_attributes_before = [memory.get(attr) for attr in self.attributes_before]
        memory_attributes_after = [memory.get(attr) for attr in self.attributes_after]
        return self.func(*memory_attributes_before, *args, *memory_attributes_after)


def add_to_memory(func: Callable[..., T], name: str, ) -> Callable[..., T]:
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


def with_memory_attribute(func, name):
        def __inner(x, memory: PipelineMemory):
            return func(x, memory.get(name))
        return use_memory(__inner)
