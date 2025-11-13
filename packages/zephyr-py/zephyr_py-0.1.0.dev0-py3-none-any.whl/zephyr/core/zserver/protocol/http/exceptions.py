class HTTPError(Exception):
    """Base class for HTTP related errors."""

    pass


class HTTPParserError(HTTPError):
    """Base class for parser related errors."""

    pass


class InvalidRequestLine(HTTPParserError):
    """Raised when the request line is malformed."""

    pass


class InvalidHeader(HTTPParserError):
    """Raised when a header is malformed."""

    pass


class InvalidChunkSize(HTTPParserError):
    """Raised when a chunk size is invalid in chunked encoding."""

    pass


class PayloadTooLarge(HTTPParserError):
    """Raised when the payload exceeds maximum allowed size."""

    pass


class BufferError(HTTPError):
    """Base class for buffer related errors."""

    pass


class BufferOverflowError(BufferError):
    """Raised when buffer size exceeds maximum allowed."""

    pass


class HTTPProtocolError(HTTPError):
    """HTTP Protocol Base error."""
