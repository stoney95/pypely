class PypelyTuple(tuple):
    """I am used to mark the output of `fork`."""

    def __new__(cls, *x):  # noqa: D102
        return super(PypelyTuple, cls).__new__(cls, x)


class PypelyError(Exception):
    """I am the parent of all errors and exceptions in pypely."""

    def __init__(self, message):
        return super(PypelyError, self).__init__(message)
