class PipelineForwardError(Exception):
    def __init__(self, message):
        super(PipelineForwardError, self).__init__(message)


class PipelineCallError(Exception):
    def __init__(self, message):
        super(PipelineCallError, self).__init__(message)