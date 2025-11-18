"""
HTTP Request Parser Implementation.

Provides a robust parser for HTTP requests and URL handling capabilities.

Created At: 08 FEB 2025
Updated At: 12 MAR 2025
Author: A M <mariesmw007@gmail.com>
"""

from __future__ import annotations

import logging
import re
import asyncio
from io import BytesIO
from typing import Optional, Dict, Tuple, List, Set, Union, Match, TYPE_CHECKING, NamedTuple, Any

from zephyr.core.zserver.protocol.http.parser.base import BaseHTTPParser, ParserCallback, BaseParser
from zephyr.core.zserver.protocol.http.constants import ParserState, HTTP_METHODS
from zephyr.core.zserver.protocol.http.exceptions import (
    HTTPParserError,
    InvalidRequestLine,
    InvalidHeader,
    InvalidChunkSize,
)
from zephyr.core.zserver.net.unreader import UnReader
from zephyr.core.logging.logger import get_logger

if TYPE_CHECKING:
    from zephyr.core.zserver.protocol.http.http import HTTPProtocol

# Constants
MAX_LINE_SIZE = 8192  # 8KB
MAX_HEADERS = 100

# Regular expressions
REQUEST_LINE_RE = re.compile(rb"^([A-Z]+) (.*) (HTTP/\d\.\d)$")
HEADER_RE = re.compile(rb"^([^:]+):\s*(.*)$")
CHUNK_SIZE_RE = re.compile(rb"^([0-9a-fA-F]+)[;]?.*$")


class URLComponents(NamedTuple):
    """URL components as defined in RFC 3986."""

    schema: str
    username: str | None
    password: str | None
    hostname: str
    port: int | None
    path: str
    query: str | None
    fragment: str | None


class HttpParser(BaseParser):
    """Enhanced base HTTP parser with common functionality."""

    def __init__(self, protocol: HTTPProtocol, unreader: UnReader | None = None):
        super().__init__()
        self.protocol = protocol
        self.unreader = unreader
        self._state = ParserState.START_LINE
        self._headers: dict[str, str] = {}
        self._body = bytearray()
        self._content_length: int | None = None
        self._chunked = False
        self._error: str | None = None

    def on_message_begin(self):
        """Callback when message parsing begins."""
        pass

    def on_header(self, name: bytes, value: bytes):
        """Callback when header is parsed."""
        self._headers[name.decode("latin1").lower()] = value.decode("latin1")

    def on_headers_complete(self):
        """Callback when headers are complete."""
        # Process content-length header
        if "content-length" in self._headers:
            try:
                self._content_length = int(self._headers["content-length"])
            except ValueError:
                self._handle_error("Invalid Content-Length header")

        # Process transfer-encoding header
        if "transfer-encoding" in self._headers:
            encodings = [x.strip() for x in self._headers["transfer-encoding"].split(",")]
            if "chunked" in encodings:
                self._chunked = True

    def on_body(self, data: bytes):
        """Callback when body chunk is parsed."""
        self._body.extend(data)

    def on_message_complete(self):
        """Callback when message is complete."""
        pass

    def _handle_error(self, message: str):
        """Handle parsing errors."""
        self._error = message
        raise HTTPParserError(message)

    def get_header(self, name: str):
        """
        Get the value of a header by its name (case-insensitive)

        Args:
            name: Header name to look up

        Returns:
            str | None: Header value if found, None otherwise
        """
        return self._headers.get(name.lower())


class LegacyHTTPRequestParser(BaseHTTPParser):
    """
    Parser for HTTP requests.

    Implements a state machine to parse HTTP request messages.
    """

    def __init__(self, callback: Optional[ParserCallback] = None):
        """
        Initialize the HTTP request parser.

        Args:
            callback: Callback object to receive parsing events
        """
        super().__init__(callback)
        self.reset()

    def reset(self) -> None:
        """Reset parser state."""
        self.state = ParserState.INITIALIZED
        self._buffer = bytearray()
        self._error = None


class HTTPRequestParser(HttpParser):
    """Enhanced HTTP request parser."""

    def __init__(self, protocol: HTTPProtocol):
        super().__init__(protocol)
        self.unreader = None
        self._method = ""
        self._path = ""
        self._version = ""
        self._max_header_size = 8192  # Configurable
        self._max_body_size = 1048576  # Configurable
        self._buffer = bytearray()
        self._error_msg = None
        self.callback = protocol
        self.state = ParserState.INITIALIZED
        self._header_count = 0
        self._is_complete = False
        self.logger = get_logger("Zephyr.error")

        self.logger.debug(f"HTTPRequestParser initialized, id: {id(self)} and state: {self.state}")

    @property
    def is_complete(self) -> bool:
        return self.state == ParserState.COMPLETE

    @is_complete.setter
    def is_complete(self, value: bool):
        self._is_complete = value
        self.logger.info(f"HTTPRequestParser is_complete set to: {value}, id: {id(self)}")

    def error(self) -> Optional[str]:
        """Return the current error message if any."""
        return self._error_msg

    @property
    def is_error(self) -> bool:
        """Check if the parser is in an error state."""
        return self._error_msg is not None

    def on_url(self, url: bytes):
        """Process URL from request line."""
        self._path = url.decode("latin1")

    def on_error(self, error: str):
        """Handle parser error."""
        self._error_msg = error

    def reset(self):
        """Reset parser state."""
        self._state = ParserState.START_LINE
        self._headers = {}
        self._body = bytearray()
        self._method = ""
        self._path = ""
        self._version = ""
        self._content_length = None
        self._chunked = False
        self._buffer = bytearray()
        self._error_msg = None
        self.state = ParserState.INITIALIZED
        self._header_count = 0
        self.is_complete = False

    def feed_data(self, data: bytes) -> None:
        """
        Feed data to the parser.

        Args:
            data: Data to parse

        Raises:
            HTTPParserError: If parsing fails
        """
        if self.is_error:
            return

        if self.is_complete:
            self.reset()

        self._buffer.extend(data)
        print(f"Buffer: {self._buffer}")

        try:
            while self._buffer:
                if self.state == ParserState.INITIALIZED:
                    self.state = ParserState.START_LINE
                    if self.callback:
                        self.callback.on_message_begin()

                if self.state == ParserState.START_LINE:
                    # Find the end of the line
                    pos = self._buffer.find(b"\r\n")
                    if pos == -1:
                        # Not enough data
                        if len(self._buffer) > MAX_LINE_SIZE:
                            raise InvalidRequestLine("Request line too long")
                        return

                    # Extract and parse the request line
                    line = bytes(self._buffer[:pos])
                    self._buffer = self._buffer[pos + 2 :]  # Remove line and CRLF

                    match = REQUEST_LINE_RE.match(line)
                    if not match:
                        raise InvalidRequestLine(f"Invalid request line: {line.decode('ascii', errors='replace')}")

                    method, url, version = match.groups()

                    # Validate method
                    method_str = method.decode("ascii")
                    if method_str not in HTTP_METHODS:
                        raise InvalidRequestLine(f"Unknown HTTP method: {method_str}")

                    # Store request information
                    self._method = method
                    self._url = url
                    self._version = version

                    # Notify callback
                    if self.callback:
                        self.callback.on_url(url)

                    # Move to headers state
                    self.state = ParserState.HEADERS

                elif self.state == ParserState.HEADERS:
                    # Find the end of headers
                    pos = self._buffer.find(b"\r\n\r\n")
                    if pos == -1:
                        # Not enough data
                        if len(self._buffer) > MAX_LINE_SIZE * MAX_HEADERS:
                            raise InvalidHeader("Headers too long")
                        return

                    # Extract headers
                    headers = self._buffer[:pos]
                    self._buffer = self._buffer[pos + 4 :]  # Remove headers and double CRLF

                    # Parse headers
                    for line in headers.split(b"\r\n"):
                        if not line:
                            continue

                        match = HEADER_RE.match(line)
                        if not match:
                            raise InvalidHeader(f"Invalid header line: {line.decode('ascii', errors='replace')}")

                        name = match.group(1).strip()
                        value = match.group(2).strip()

                        self._header_count += 1
                        self._headers[name.lower().decode()] = value.decode()
                        if self._header_count > MAX_HEADERS:
                            raise InvalidHeader("Too many headers")

                        if self.callback:
                            self.callback.on_header(name, value)

                    # Process special headers
                    self._content_length = int(self.get_header("content-length") or 0)

                    self._chunked = self.get_header("transfer-encoding") == "chunked"

                    # Notify headers complete
                    if self.callback:
                        self.callback.on_headers_complete()

                    # Move to body state or complete
                    if self._content_length == 0 and not self._chunked:
                        self.state = ParserState.COMPLETE
                        if self.callback:
                            self.callback.on_message_complete()
                        return

                    self.state = ParserState.BODY

                elif self.state == ParserState.BODY:
                    if self._chunked:
                        if not self._parse_chunked_body():
                            return
                    else:
                        if not self._parse_body():
                            return

                    # Message complete
                    self.state = ParserState.COMPLETE
                    if self.callback:
                        self.callback.on_message_complete()
                    return

                elif self.state == ParserState.COMPLETE:
                    return
            print(f"Buffer: {self._buffer}")

        except Exception as e:
            self._set_error(str(e))
            raise HTTPParserError(str(e)) from e

    def _parse_request_line(self, line: bytes) -> None:
        match = REQUEST_LINE_RE.match(line)
        if not match:
            self._handle_error("Invalid request line")

        self._method = match.group(1).decode("ascii")
        if self._method not in HTTP_METHODS:
            self._handle_error(f"Unsupported method: {self._method}")

        self.callback.on_url(match.group(2))
        self._version = match.group(3).decode("ascii")

    def _parse_headers(self, headers: bytes) -> None:
        for line in headers.split(b"\r\n"):
            if not line:
                continue

            match = HEADER_RE.match(line)
            if not match:
                self._handle_error("Invalid header line")

            name = match.group(1).strip()
            value = match.group(2).strip()

            self._header_count += 1
            if self._header_count > MAX_HEADERS:
                self._handle_error("Too many headers")

            self.callback.on_header(name, value)

    def _parse_body(self) -> bool:
        """Parse fixed-length body.

        Returns:
            bool: True if body is complete, False if more data needed
        """
        if self._content_length is None:
            raise HTTPParserError("No content length specified")

        remaining = self._content_length - len(self._body)
        body_data = self._buffer[:remaining]
        self._buffer = self._buffer[remaining:]

        if self.callback:
            self.callback.on_body(body_data)
        self._body.extend(body_data)

        return len(self._body) >= self._content_length

    def _parse_chunked_body(self) -> bool:
        """Parse chunked body.

        Returns:
            bool: True if body is complete, False if more data needed
        """
        while self._buffer:
            # Read chunk size
            pos = self._buffer.find(b"\r\n")
            if pos == -1:
                return False

            line = self._buffer[:pos]
            rest = self._buffer[pos + 2 :]

            match = CHUNK_SIZE_RE.match(line)
            if not match:
                raise HTTPParserError("Invalid chunk size")

            size = int(match.group(1), 16)
            if size == 0:
                self._buffer = rest
                return True

            # Read chunk data
            if len(rest) < size + 2:
                return False

            body_data = rest[:size]
            self._buffer = rest[size + 2 :]  # Skip CRLF

            if self.callback:
                self.callback.on_body(body_data)
            self._body.extend(body_data)

        return False
        """Process HTTP headers."""
        while True:
            # Find the end of the line
            pos = self._buffer.find(b"\r\n")
            if pos == -1:
                # Not enough data
                if len(self._buffer) > MAX_LINE_SIZE:
                    raise InvalidHeader("Header line too long")
                return

            # Check for end of headers
            if pos == 0:
                # Empty line, end of headers
                del self._buffer[:2]  # Remove CRLF

                # Process special headers
                self._process_special_headers()

                # Notify callback
                if self.callback:
                    self.callback.on_headers_complete()

                # Move to body state
                if self._chunked:
                    self.state = ParserState.CHUNK_LENGTH
                else:
                    self.state = ParserState.BODY
                return

            # Extract and parse the header
            line = bytes(self._buffer[:pos])
            del self._buffer[: pos + 2]  # Remove line and CRLF

            match = HEADER_RE.match(line)
            if not match:
                raise InvalidHeader(f"Invalid header line: {line.decode('ascii', errors='replace')}")

            name, value = match.groups()

            # Limit header count
            self._header_count += 1
            if self._header_count > MAX_HEADERS:
                raise InvalidHeader("Too many headers")

            # Normalize header name (lowercase)
            name_str = name.decode("ascii").lower()
            value_str = value.decode("ascii")

            # Store header
            self._headers[name_str] = value_str

            # Notify callback
            if self.callback:
                self.callback.on_header(name_str, value_str)

    def _process_special_headers(self) -> None:
        """Process special headers that affect parsing."""
        # Check for Content-Length
        if "content-length" in self._headers:
            try:
                self._content_length = int(self._headers["content-length"])
                if self._content_length < 0:
                    raise ValueError("Negative content length")
            except ValueError:
                raise InvalidHeader("Invalid Content-Length header")

        # Check for Transfer-Encoding
        if "transfer-encoding" in self._headers:
            encodings = [x.strip() for x in self._headers["transfer-encoding"].split(",")]
            if "chunked" in encodings:
                self._chunked = True

    def _process_body(self) -> None:
        """Process HTTP message body."""
        # If no content length and not chunked, body is empty
        if self._content_length is None and not self._chunked:
            self._complete_message()
            return

        # If we have a content length, read that many bytes
        self._body_bytes_read = 0
        if self._content_length is not None:
            remaining = self._content_length - self._body_bytes_read

            if len(self._buffer) >= remaining:
                # We have all the data
                body_data = bytes(self._buffer[:remaining])
                del self._buffer[:remaining]
                self._body_bytes_read += len(body_data)

                # Notify callback
                if self.callback and body_data:
                    self.callback.on_body(body_data)

                # Complete message
                self._complete_message()
            else:
                # We need more data
                body_data = bytes(self._buffer)
                self._buffer.clear()
                self._body_bytes_read += len(body_data)

                # Notify callback
                if self.callback and body_data:
                    self.callback.on_body(body_data)

    def _process_chunk_length(self) -> None:
        """Process chunk length line in chunked encoding."""
        # Find the end of the line
        pos = self._buffer.find(b"\r\n")
        if pos == -1:
            # Not enough data
            if len(self._buffer) > MAX_LINE_SIZE:
                raise InvalidChunkSize("Chunk size line too long")
            return

        # Extract and parse the chunk size line
        line = bytes(self._buffer[:pos])
        del self._buffer[: pos + 2]  # Remove line and CRLF

        match = CHUNK_SIZE_RE.match(line)
        if not match:
            raise InvalidChunkSize(f"Invalid chunk size: {line.decode('ascii', errors='replace')}")

        # Parse chunk size (hex)
        try:
            self._chunk_size = int(match.group(1), 16)
        except ValueError:
            raise InvalidChunkSize(f"Invalid chunk size: {line.decode('ascii', errors='replace')}")

        # Check for last chunk
        if self._chunk_size == 0:
            # Last chunk, skip trailer and complete message
            self._process_chunk_end()
        else:
            # Move to chunk data state
            self.state = ParserState.CHUNK_DATA

    def _process_chunk_data(self) -> None:
        """Process chunk data in chunked encoding."""
        if len(self._buffer) < self._chunk_size + 2:
            # Not enough data
            return

        # Extract chunk data
        chunk_data = bytes(self._buffer[: self._chunk_size])

        # Check for chunk end (CRLF)
        if self._buffer[self._chunk_size : self._chunk_size + 2] != b"\r\n":
            raise InvalidChunkSize("Missing CRLF after chunk data")

        # Remove chunk data and CRLF
        del self._buffer[: self._chunk_size + 2]

        # Notify callback
        if self.callback and chunk_data:
            self.callback.on_body(chunk_data)

        # Move back to chunk length state for next chunk
        self.state = ParserState.CHUNK_LENGTH

    def _process_chunk_end(self) -> None:
        """Process the end of chunked encoding (trailers)."""
        # Process trailers (additional headers)
        while True:
            # Find the end of the line
            pos = self._buffer.find(b"\r\n")
            if pos == -1:
                # Not enough data
                return

            # Check for end of trailers
            if pos == 0:
                # Empty line, end of trailers
                del self._buffer[:2]  # Remove CRLF
                self._complete_message()
                return

            # Extract and process trailer line
            line = bytes(self._buffer[:pos])
            del self._buffer[: pos + 2]  # Remove line and CRLF

            # Parse trailer as header
            match = HEADER_RE.match(line)
            if match:
                name, value = match.groups()
                name_str = name.decode("ascii").lower()
                value_str = value.decode("ascii")

                # Update headers
                self._headers[name_str] = value_str

                # Notify callback
                if self.callback:
                    self.callback.on_header(name_str, value_str)

    def _complete_message(self) -> None:
        """Complete HTTP message parsing."""
        self.state = ParserState.COMPLETE
        self.is_complete = True

        # Notify callback
        if self.callback:
            self.callback.on_message_complete()

    def _set_error(self, error: str) -> None:
        """
        Set parser error.

        Args:
            error: Error description
        """
        self.state = ParserState.ERROR
        self._error_msg = error

        # Notify callback
        if self.callback:
            self.callback.on_error(error)

    def get_http_version(self):
        """Return the HTTP version of the request."""
        return self._version

    def should_keep_alive(self):
        """Determine if the connection should be kept alive."""
        if self._version == "HTTP/1.0":
            return "connection" in self._headers and self._headers["connection"].lower() == "keep-alive"
        else:  # HTTP/1.1+
            return "connection" not in self._headers or self._headers["connection"].lower() != "close"

    def get_method(self):
        """Return the HTTP method of the request."""
        return self._method

    def get_parsed_data(self):
        """Return parsed HTTP request data."""
        if not self.is_complete:
            return None

        return {
            "method": self._method,
            "path": self._path,
            "version": self._version,
            "headers": self._headers,
            "body": bytes(self._body),
        }

    def parse_url(self, url: str):
        """
        Parse URL into components following RFC 3986

        Args:
            url: URL string to parse

        Returns:
            URLComponents named tuple containing all URL parts

        Example URLs:
            - http://example.com
            - https://user:pass@example.com:8080/path?query=value#fragment
            - //example.com/path
            - /absolute/path
            - relative/path
        """
        # Default values
        schema = ""
        username = None
        password = None
        hostname = ""
        port = None
        path = ""
        query = None
        fragment = None

        # Extract fragment
        if "#" in url:
            url, fragment = url.split("#", 1)

        # Extract query
        if "?" in url:
            url, query = url.split("?", 1)

        # Extract schema
        if "://" in url:
            schema, url = url.split("://", 1)
        elif url.startswith("//"):
            url = url[2:]  # Remove leading //

        # Extract authority (user:pass@host:port)
        if "/" in url:
            authority, path = url.split("/", 1)
            path = "/" + path
        else:
            authority = url
            path = "/"

        # Extract user info
        if "@" in authority:
            userinfo, authority = authority.split("@", 1)
            if ":" in userinfo:
                username, password = userinfo.split(":", 1)
            else:
                username = userinfo

        # Extract port
        if ":" in authority:
            hostname, port_str = authority.split(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                pass
        else:
            hostname = authority

        return URLComponents(
            schema=schema,
            username=username,
            password=password,
            hostname=hostname,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
        )

    def is_valid_hostname(self, hostname: str):
        """
        Validate hostname according to RFC 1123

        Args:
            hostname: Hostname to validate

        Returns:
            bool: True if hostname is valid
        """
        if not hostname:
            return False

        if len(hostname) > 255:
            return False

        # Simple validation - more complex validation would use regex
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.")
        return all(c in allowed_chars for c in hostname)

    def join_url(self, base: str, url: str):
        """
        Join base URL with relative URL following RFC 3986

        Args:
            base: Base URL
            url: URL to join (can be relative or absolute)

        Returns:
            str: Joined URL
        """
        # If url is absolute, return it as is
        if "://" in url or url.startswith("//"):
            return url

        # Parse base URL
        base_components = self.parse_url(base)

        # If url starts with /, it's absolute path
        if url.startswith("/"):
            return f"{base_components.schema}://{base_components.hostname}{':' + str(base_components.port) if base_components.port else ''}{url}"

        # It's a relative path, join with base path
        base_path = base_components.path
        if not base_path.endswith("/"):
            base_path = "/".join(base_path.split("/")[:-1]) + "/"

        return f"{base_components.schema}://{base_components.hostname}{':' + str(base_components.port) if base_components.port else ''}{base_path}{url}"

    def should_upgrade(self):
        """Check if connection should be upgraded (e.g., to WebSocket)."""
        return (
            "upgrade" in self._headers
            and "connection" in self._headers
            and "upgrade" in self._headers["connection"].lower()
        )
