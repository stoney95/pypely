class MemoryAttributeExistsError(AttributeError):
    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryAttributeNotFoundError(AttributeError):
    def __init__(self, message):
        super(AttributeError, self).__init__(message)


class MemoryIngestNotAllowedError(RuntimeError):
    def __init__(self, message):
        super(RuntimeError, self).__init__(message)