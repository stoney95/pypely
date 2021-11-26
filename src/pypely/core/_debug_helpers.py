from collections import namedtuple
from typing import Callable
from pypely.core.errors import PipelineCallError, PipelineForwardError

DebugMemory = namedtuple('DebugMemory', ['combine', 'first', 'last'])

def debugable_reduce(debug_memory: DebugMemory, func2: Callable):
    def _combine(*args):
        _first = _try(debug_memory.combine, debug_memory, PipelineCallError)
        _second = _try(func2, debug_memory, PipelineForwardError)

        return _second(_first(*args))

    return DebugMemory(combine=_combine, last=func2, first=debug_memory.first)


def _try(func, debug_memory, error_cls):
    def wrapper(*args):
        try:
            return func(*args)
        except TypeError:
            raise error_cls(debug_memory, func, args)

    return wrapper
