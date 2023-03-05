"""I describe all errors that can occur during memory interaction."""

from pypely._types import PypelyError


class MemoryAttributeExistsError(AttributeError, PypelyError):
    """I will be raised if a memory entry already exists."""

    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryAttributeNotFoundError(AttributeError, PypelyError):
    """I will be raised if no memory entry with a given name exists."""

    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryIngestNotAllowedError(RuntimeError, PypelyError):
    """I will be raised if a memory entry is ingested into a function that does not allow this."""

    def __init__(self, message):
        super(RuntimeError, self).__init__(message)


class MemoryTypeDoesNotMatchError(RuntimeError, PypelyError):
    """I will be rasie if the type of a memory entry does not match the parameter type it should be ingested for."""

    def __init__(self, message):
        super(RuntimeError, self).__init__(message)


class InvalidMemoryAttributeError(AttributeError, PypelyError):
    """I will be raised if a value that is ingested into the memory has an invalid type."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NoFreeParameterFound(AttributeError, PypelyError):
    """I am raised when there are too many ingests into a function."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
