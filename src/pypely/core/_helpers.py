import inspect
from collections import namedtuple, defaultdict
from typing import Callable
from pypely.core.errors import PipelineCallError, PipelineForwardError

DebugMemory = namedtuple('DebugMemory', ['combine', 'first', 'last'])

def debugable_reduce(debug_memory: DebugMemory, func2: Callable):
    def _combine(*args):
        _first = _try(debug_memory.combine, debug_memory, PipelineCallError, call_error_message)
        _second = _try(func2, debug_memory, PipelineForwardError, forward_error_message)

        return _second(_first(*args))

    return DebugMemory(combine=_combine, last=func2, first=debug_memory.first)



def call_error_message(func, debug_memory, used_args):
    return "\n".join([
        f"Given arguments do not match '{debug_memory.first.__name__}' arguments.",
        f"  Given arguments: {used_args}",
        f"  '{debug_memory.first.__name__}' consumes: {format_args(debug_memory.first)}",
        f"  {func_details(debug_memory.first)}"
    ])


def forward_error_message(func, debug_memory, used_args):
    return "\n".join([
        f"Returned value of '{debug_memory.last.__name__}' does not match the arguement of '{func.__name__}'.",
        f"  '{debug_memory.last.__name__}' returned: {used_args}",
        f"  '{func.__name__}' consumes: {format_args(func)}",
        f"  {func_details(debug_memory.last)}",
        f"  {func_details(func)}"
    ])


def format_args(func):
    argspec = inspect.getfullargspec(func)
    annotations = defaultdict(lambda: None)
    for k, v in argspec.annotations.items():
        annotations[k] = v

    def _annotate(annotation):
        if annotation is None:
            return ""
        return f": {annotation}"

    args = ', '.join([f'{x}{_annotate(annotations[x])}' for x in argspec.args])
    return f'({args})'


def func_details(func):
    return f"'{func.__name__}' from File \"{func.__code__.co_filename}\", line {func.__code__.co_firstlineno}"


def _try(func, debug_memory, error_cls, error_message_func):
    def wrapper(*args):
        try:
            return func(*args)
        except TypeError:
            error_msg = error_message_func(func, debug_memory, args)
            raise error_cls(error_msg)

    return wrapper
