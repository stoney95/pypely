from collections import namedtuple
from typing import Callable

from pypely.core.errors import PipelineCallError, PipelineForwardError, PipelineStepError
from pypely._types import PypelyError

DebugMemory = namedtuple('DebugMemory', ['combine', 'first', 'last'])
ExceptionSubstitution = namedtuple('ExceptionSubstitution', ['exception', 'pypely_error'])

def debugable_reduce(debug_memory: DebugMemory, func2: Callable):
    def _combine(*args):
        _first = _try(
            debug_memory.combine, 
            debug_memory, 
            PipelineCallError
        )
        
        _second = _try(
            func2, 
            debug_memory, 
            PipelineForwardError
        )

        return _second(_first(*args))

    return DebugMemory(combine=_combine, last=func2, first=debug_memory.first)


def _try(func: Callable, debug_memory: DebugMemory, type_error_handler):
    def wrap(*args):
        try:
            return func(*args)
        except TypeError:
            raise type_error_handler(debug_memory, func, args)
        except Exception as e:
            if isinstance(e, PypelyError):
                raise e
            raise PipelineStepError(debug_memory, func, args)

    return wrap
