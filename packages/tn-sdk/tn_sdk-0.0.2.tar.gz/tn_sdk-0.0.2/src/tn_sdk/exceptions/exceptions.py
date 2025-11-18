class TnApiException(Exception):
    """
    Base class for all Trip Ninja SDK exceptions.

    :param message: Human-readable error message
    :param code: Optional error code (similar to API error codes)
    """

    DEFAULT_MESSAGE = "Fallback error message for Trip Ninja SDK"
    DEFAULT_CODE = "SDK_ERROR"

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        code: str = DEFAULT_CODE,
    ):
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self):
        return f"[{self.code}] {self.message}"


class InvalidDataException(TnApiException):
    """Raised when invalid or malformed data is passed to an SDK function."""

    DEFAULT_MESSAGE = "Invalid or malformed data"
    DEFAULT_CODE = "INVALID_DATA"

    def __init__(self, message: str = DEFAULT_MESSAGE, code: str = DEFAULT_CODE):
        super().__init__(message, code=code)
