from ast import Call
from email import message
import inspect
import re
from typing import Any, Callable, Optional
from pypely.core.errors._formating import format_return_type_annotation, format_parameter_signature, func_details
from pypely._types import PypelyError


class PipelineStepError(PypelyError):
    def __init__(self, func: Callable, exception: Exception):
        message = self.__error_message(func, exception)
        super(PipelineStepError, self).__init__(message)

    def __error_message(self, func: Callable, exception: Exception):
        return "\n".join([
            f"The step {func_details(func)} failed",
            f"  The occurred exception is: {exception}"
        ])


class PipelineForwardError(PypelyError):
    def __init__(self, debug_memory, func, used_args):
        message = self.__error_message(debug_memory, func, used_args)
        super(PipelineForwardError, self).__init__(message)

    def __error_message(self, debug_memory, func, used_args):
        return "\n".join([
            f"Returned value of '{debug_memory.last.__name__}' does not match the arguement of '{func.__name__}'.",
            f"  '{debug_memory.last.__name__}' returned: {used_args}",
            f"  '{func.__name__}' consumes: {format_parameter_signature(func)}",
            f"  {func_details(debug_memory.last)}",
            f"  {func_details(func)}"
        ])


class PipelineCallError(PypelyError):
    def __init__(self, debug_memory, func, used_args):
        message = self.__error_message(debug_memory, func, used_args)
        super(PipelineCallError, self).__init__(message)

    def __error_message(self, debug_memory, func, used_args):
        return "\n".join([
            f"Given arguments do not match '{debug_memory.first.__name__}' arguments.",
            f"  Given arguments: {used_args}",
            f"  '{debug_memory.first.__name__}' consumes: {format_parameter_signature(debug_memory.first)}",
            f"  {func_details(debug_memory.first)}"
        ])


class ParameterAnnotationsMissingError(PypelyError):
    def __init__(self, func: Callable):
        message = self.__error_message(func)
        super().__init__(message)

    def __error_message(self, func: Callable) -> str:
        return "\n".join([
            f"Parameter annotations are missing for {func_details(func)}",
            f"  pypely relies on annotations to match function input and output of consecutive functions.",
            f"  Please provide type annotations to the parameters of the given function."
        ])


class ReturnTypeAnnotationMissingError(PypelyError):
    def __init__(self, func: Callable):
        message = self.__error_message(func)
        super().__init__(message)

    def __error_message(self, func: Callable) -> str:
        return "\n".join([
            f"Return type is missing for {func_details(func)}",
            f"  pypely relies on annotations to match function input and output of consecutive functions.",
            f"  Please provide the return type annotation of the given function."
        ])


class InvalidParameterAnnotationError(PypelyError):
    def __init__(self, func: Callable, param: inspect.Parameter):
        message = self.__error_message(func, param)
        super().__init__(message)

    def __error_message(self, func: Callable, param: inspect.Parameter) -> str:
        return "\n".join([
            f"Parameter annotation is invalid for {func_details(func)}",
            f"  Parameter {param.name} has annotation {param.annotation}."
            f"  Annotation of kind {param.kind} is currently not supported."
        ])


class OutputInputDoNotMatchError(PypelyError):
    def __init__(self, func1: Callable, func2: Callable, inner_exception: Optional[Exception]=None):
        message = self.__error_message(func1, func2, inner_exception)
        super().__init__(message)

    def __error_message(self, func1: Callable, func2: Callable, inner_exception: Optional[Exception]=None) -> str:
        return_type = format_return_type_annotation(func1)
        expected_parameters = format_parameter_signature(func2)

        msg = [
            f"{func_details(func2)} couldn't be added to the pipeline.",
            f"  The provided output at this stage of the pipeline has this format: {return_type}.",
            f"  The provided function expects these parameters: {expected_parameters}.",
            f"  Please adjust either the output or the input types."
        ]

        if inner_exception is not None:
            msg.append(f"  This error was raised due to an inner exception: {inner_exception}")

        return "\n".join(msg)