class PypelyTuple(tuple):
    
    def __new__(cls, *x):
        return super(PypelyTuple, cls).__new__(cls, x)


class PypelyError(Exception):
    def __init__(self, message):
        return super(PypelyError, self).__init__(message)