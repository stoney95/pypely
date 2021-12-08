from pypely.core.errors._formating import format_args, func_details
from pypely._types import PypelyError


class PipelineStepError(PypelyError):
    def __init__(self, debug_memory, func, used_args):
        message = self.__error_message(debug_memory, func, used_args)
        super(PipelineStepError, self).__init__(message)

    def __error_message(self, debug_memory, func, used_args):
        return "\n".join([
            f"The step with name '{func.__name__}' failed",
            f"  The last step before the failed step was '{debug_memory.last.__name__}'",
            f"  {func_details(debug_memory.last)}",
            f"  {func_details(func)}"
        ])


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