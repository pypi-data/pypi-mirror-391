"""
HTTP Parser Base Classes.

Defines the base interfaces for HTTP parsers and callbacks.

Created At: 08 FEB 2025
Author: A M <mariesmw007@gmail.com>
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol

from zephyr.core.zserver.protocol.http.constants import ParserState
from ....net.unreader import UnReader
from ....net.connection import Connection


class ParserCallback(Protocol):
    """
    Protocol defining callback methods for HTTP parsing events.

    Implementations receive notifications about parsed HTTP elements.
    """

    def on_message_begin(self) -> None:
        """Called when message parsing begins."""
        ...

    def on_url(self, url: bytes) -> None:
        """
        Called when URL is parsed in a request.

        Args:
            url: The URL bytes
        """
        ...

    def on_header(self, name: str, value: str) -> None:
        """
        Called when a header is parsed.

        Args:
            name: Header name (lowercase)
            value: Header value
        """
        ...

    def on_headers_complete(self) -> None:
        """Called when all headers have been parsed."""
        ...

    def on_body(self, data: bytes) -> None:
        """
        Called when body data is parsed.

        Args:
            data: Body data chunk
        """
        ...

    def on_message_complete(self) -> None:
        """Called when the entire message has been parsed."""
        ...

    def on_error(self, error: str) -> None:
        """
        Called when a parsing error occurs.

        Args:
            error: Error description
        """
        ...


class BaseParser(ABC):
    """Legacy base parser class for backward compatibility."""

    @abstractmethod
    def feed_data(self, data: bytes) -> None:
        """Feed data to the parser."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset parser state."""
        pass

    @abstractmethod
    def error(self) -> Optional[str]:
        """Get the current error if any."""
        pass

    @abstractmethod
    def is_error(self) -> bool:
        """Check if parser is in error state."""
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        """Check if parsing is complete."""
        pass


class BaseHTTPParser(ABC):
    """
    Abstract base class for HTTP parsers.

    Defines the interface for HTTP request and response parsers.
    """

    def __init__(self, callback: Optional[ParserCallback] = None, connection: Optional[Connection] = None):
        """
        Initialize parser.

        Args:
            callback: Callback object to receive parsing events
            connection: Optional Connection for streaming data
        """
        self.callback = callback
        self.connection = connection
        self.state = ParserState.INITIALIZED
        self._buffer = bytearray()
        self._error: Optional[str] = None
        self.unreader = UnReader(connection) if connection else None

    @abstractmethod
    def feed_data(self, data: bytes) -> None:
        """
        Feed data to the parser.

        Args:
            data: Data to parse
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset parser state."""
        pass

    @property
    def error(self) -> Optional[str]:
        """Get the current error if any."""
        return self._error

    @property
    def is_error(self) -> bool:
        """Check if parser is in error state."""
        return self.state == ParserState.ERROR

    @property
    def is_complete(self) -> bool:
        """Check if parsing is complete."""
        return self.state == ParserState.COMPLETE
