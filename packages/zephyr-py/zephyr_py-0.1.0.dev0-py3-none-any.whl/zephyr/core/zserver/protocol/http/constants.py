from enum import Enum, auto


class ParserState(Enum):
    """
    Enumeration of HTTP parser states.
    """

    INITIALIZED = auto()  # Initial state when parser is created
    START_LINE = auto()  # Parsing the first line (request/response line)
    HEADERS = auto()  # Parsing HTTP headers
    BODY = auto()  # Parsing message body
    CHUNK_LENGTH = auto()
    CHUNK_DATA = auto()
    CHUNK_END = auto()
    COMPLETE = auto()  # Parsing is complete
    ERROR = auto()  # Error occurred during parsing


# HTTP Methods
HTTP_METHODS = frozenset(["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "TRACE", "CONNECT", "PATCH"])

# Default configuration values
DEFAULT_MAX_HEADER_SIZE = 8192  # 8KB
DEFAULT_MAX_BODY_SIZE = 1048576  # 1MB
DEFAULT_BUFFER_SIZE = 8192  # 8KB
MAX_REQUEST_LINE_SIZE = 8192  # 8KB

# HTTP Version constants
HTTP_1_0 = "HTTP/1.0"
HTTP_1_1 = "HTTP/1.1"

# Common HTTP header names
CONTENT_LENGTH = "content-length"
TRANSFER_ENCODING = "transfer-encoding"
CONNECTION = "connection"
CONTENT_TYPE = "content-type"
HOST = "host"
USER_AGENT = "user-agent"
ACCEPT = "accept"
ACCEPT_ENCODING = "accept-encoding"
ACCEPT_LANGUAGE = "accept-language"
COOKIE = "cookie"
SET_COOKIE = "set-cookie"
LOCATION = "location"
AUTHORIZATION = "authorization"

# Content types
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"
CONTENT_TYPE_MULTIPART = "multipart/form-data"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_HTML = "text/html"
CONTENT_TYPE_XML = "application/xml"
CONTENT_TYPE_BINARY = "application/octet-stream"

# Connection values
CONNECTION_CLOSE = "close"
CONNECTION_KEEP_ALIVE = "keep-alive"

# Common status codes with reason phrases
STATUS_PHRASES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    204: "No Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    429: "Too Many Requests",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}

# HTTP/1.1 status line format
STATUS_LINE_FORMAT = "HTTP/1.1 {status} {phrase}\r\n"

# Pre-computed status lines for common status codes
STATUS_LINE = {
    status: STATUS_LINE_FORMAT.format(status=status, phrase=phrase).encode("ascii")
    for status, phrase in STATUS_PHRASES.items()
}

# Default headers
DEFAULT_SERVER_HEADER = "Zephyr/1.0"
DEFAULT_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

# Flow control
DEFAULT_HIGH_WATER_MARK = 65536  # 64KB
DEFAULT_LOW_WATER_MARK = 16384  # 16KB
