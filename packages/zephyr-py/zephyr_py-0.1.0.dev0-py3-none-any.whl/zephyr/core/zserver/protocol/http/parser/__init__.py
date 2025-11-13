"""
HTTP Parser Package.

Provides parsers for HTTP requests and responses.

Created At: 08 FEB 2025
Updated At: 12 MAR 2025
Author: A M <mariesmw007@gmail.com>
"""

# Base parser components
from .base import ParserCallback, BaseHTTPParser, BaseParser
from zephyr.core.zserver.protocol.http.constants import ParserState

# HTTP parser components
from .parser import HttpParser, HTTPRequestParser, URLComponents, LegacyHTTPRequestParser

# Alias for backward compatibility
HTTPParser = HttpParser

__all__ = [
    # Base components
    "ParserCallback",
    "ParserState",
    "BaseHTTPParser",
    "BaseParser",
    # HTTP parser components
    "HttpParser",
    "HTTPRequestParser",
    "URLComponents",
    "HTTPParser",  # Alias for HttpParser
    # Legacy components
    "LegacyHTTPRequestParser",
]
