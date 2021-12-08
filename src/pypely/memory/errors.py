from pypely._types import PypelyError


class MemoryAttributeExistsError(AttributeError, PypelyError):
    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryAttributeNotFoundError(AttributeError, PypelyError):
    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryIngestNotAllowedError(RuntimeError, PypelyError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(message)