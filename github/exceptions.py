class Error(Exception):
    """Base class for exceptions."""
    pass


class ResponseError(Error):
    """Exception raised for errors in the request response."""
    def __init__(self, message):
        self.message = message
