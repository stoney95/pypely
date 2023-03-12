"""I am a collection of errors that can occur when interacting with the core of pypely."""

import inspect
from email import message
from typing import Callable, Optional

from pypely._types import PypelyError
from pypely.core.errors._formating import format_parameter_signature, format_return_type_annotation, func_details


class PipelineStepError(PypelyError):
    """I will be raised when a step inside a pipeline fails."""

    def __init__(self, func: Callable, exception: Exception):
        message = self.__error_message(func, exception)
        super(PipelineStepError, self).__init__(message)

    def __error_message(self, func: Callable, exception: Exception):
        return "\n".join([f"The step {func_details(func)} failed", f"  The occurred exception is: {exception}"])


class ParameterAnnotationsMissingError(PypelyError):
    """I will be raised if at least one parameter of the function is not type annotated."""

    def __init__(self, func: Callable):
        message = self.__error_message(func)
        super().__init__(message)

    def __error_message(self, func: Callable) -> str:
        return "\n".join(
            [
                f"Parameter annotations are missing for {func_details(func)}",
                f"  pypely relies on annotations to match function input and output of consecutive functions.",
                f"  Please provide type annotations to the parameters of the given function.",
            ]
        )


class ReturnTypeAnnotationMissingError(PypelyError):
    """I will be raised if a function has no return type annotation."""

    def __init__(self, func: Callable):
        message = self.__error_message(func)
        super().__init__(message)

    def __error_message(self, func: Callable) -> str:
        return "\n".join(
            [
                f"Return type is missing for {func_details(func)}",
                f"  pypely relies on annotations to match function input and output of consecutive functions.",
                f"  Please provide the return type annotation of the given function.",
            ]
        )


class InvalidParameterAnnotationError(PypelyError):
    """I will be rasied when an invalid parameter annotation is used."""

    def __init__(self, func: Callable, param: inspect.Parameter):
        message = self.__error_message(func, param)
        super().__init__(message)

    def __error_message(self, func: Callable, param: inspect.Parameter) -> str:
        return "\n".join(
            [
                f"Parameter annotation is invalid for {func_details(func)}",
                f"  Parameter {param.name} has annotation {param.annotation}."
                f"  Annotation of kind {param.kind} is currently not supported.",
            ]
        )


class OutputInputDoNotMatchError(PypelyError):
    """I will be raised when the output does not match the input of the following function."""

    def __init__(self, func1: Callable, func2: Callable, inner_exception: Optional[Exception] = None):
        message = self.__error_message(func1, func2, inner_exception)
        super().__init__(message)

    def __error_message(self, func1: Callable, func2: Callable, inner_exception: Optional[Exception] = None) -> str:
        return_type = format_return_type_annotation(func1)
        expected_parameters = format_parameter_signature(func2)

        msg = [
            f"{func_details(func2)} couldn't be added to the pipeline.",
            f"  The provided output at this stage of the pipeline has this format: {return_type}.",
            f"  The provided function expects these parameters: {expected_parameters}.",
            f"  Please adjust either the output or the input types.",
        ]

        if inner_exception is not None:
            msg.append(f"  This error was raised due to an inner exception: {inner_exception}")

        return "\n".join(msg)
