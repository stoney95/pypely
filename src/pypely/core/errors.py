import inspect
from collections import defaultdict

class PipelineForwardError(Exception):
    def __init__(self, debug_memory, func, used_args):
        message = self.__error_message(debug_memory, func, used_args)
        super(PipelineForwardError, self).__init__(message)


    def __error_message(self, debug_memory, func, used_args):
        return "\n".join([
            f"Returned value of '{debug_memory.last.__name__}' does not match the arguement of '{func.__name__}'.",
            f"  '{debug_memory.last.__name__}' returned: {used_args}",
            f"  '{func.__name__}' consumes: {format_args(func)}",
            f"  {func_details(debug_memory.last)}",
            f"  {func_details(func)}"
        ])


class PipelineCallError(Exception):
    def __init__(self, debug_memory, func, used_args):
        message = self.__error_message(debug_memory, func, used_args)
        super(PipelineCallError, self).__init__(message)

    def __error_message(self, debug_memory, func, used_args):
        return "\n".join([
            f"Given arguments do not match '{debug_memory.first.__name__}' arguments.",
            f"  Given arguments: {used_args}",
            f"  '{debug_memory.first.__name__}' consumes: {format_args(debug_memory.first)}",
            f"  {func_details(debug_memory.first)}"
        ])


class MergeError(Exception):
    def __init__(self, func, used_args):
        message = self.__error_message(func, used_args)
        super(MergeError, self).__init__(message)

    def __error_message(self, func, used_args):
        return "\n".join([
            f"Given arguments do not match '{func.__name__}' arguments",
            f"  Given arguments: {used_args}",
            f"  '{func.__name__}' consumes: {format_args(func)}",
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

