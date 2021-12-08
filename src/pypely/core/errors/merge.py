from pypely.core.errors._formating import format_args, func_details
from pypely._types import PypelyError


class MergeError(PypelyError):
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