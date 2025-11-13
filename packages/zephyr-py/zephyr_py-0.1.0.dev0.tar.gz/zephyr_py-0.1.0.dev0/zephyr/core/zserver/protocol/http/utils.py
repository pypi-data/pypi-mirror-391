"""HTTP Utility Functions.

Provides helper functions for HTTP protocol handling.
"""

import asyncio
import time
import socket
import urllib
from typing import Optional, Tuple, Dict, Any, List

from zephyr._types import WWWScope


def get_remote_addr(transport: asyncio.Transport) -> Optional[Tuple[str, int]]:
    """
    Get remote address from transport.

    Args:
        transport: The asyncio transport

    Returns:
        Tuple of (host, port) or None if not available
    """
    socket_info = transport.get_extra_info("socket")
    if socket_info is not None:
        try:
            info = socket_info.getpeername()
            return (str(info[0]), int(info[1])) if isinstance(info, tuple) else None
        except OSError:
            # This case appears to inconsistently occur with uvloop
            # bound to a unix domain socket.
            return None

    info = transport.get_extra_info("peername")
    if info is not None and isinstance(info, (list, tuple)) and len(info) == 2:
        return (str(info[0]), int(info[1]))
    return None


def get_local_addr(transport: asyncio.Transport) -> Optional[Tuple[str, int]]:
    """
    Get local address from transport.

    Args:
        transport: The asyncio transport

    Returns:
        Tuple of (host, port) or None if not available
    """
    socket_info = transport.get_extra_info("socket")
    if socket_info is not None:
        info = socket_info.getsockname()
        return (str(info[0]), int(info[1])) if isinstance(info, tuple) else None

    info = transport.get_extra_info("sockname")
    if info is not None and isinstance(info, (list, tuple)) and len(info) == 2:
        return (str(info[0]), int(info[1]))
    return None


def format_http_date(timestamp: float) -> str:
    """
    Format a timestamp as an HTTP date string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted HTTP date string
    """
    date_format = "%a, %d %b %Y %H:%M:%S GMT"
    return time.strftime(date_format, time.gmtime(timestamp))


def parse_headers(header_lines: List[str]) -> Dict[str, str]:
    """
    Parse HTTP headers from list of header lines.

    Args:
        header_lines: List of header lines

    Returns:
        Dictionary of headers with lowercase names
    """
    headers = {}
    for line in header_lines:
        if not line:
            continue

        try:
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()
        except ValueError:
            # Skip invalid headers
            continue

    return headers


def get_content_type(headers: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """
    Parse Content-Type header into media type and parameters.

    Args:
        headers: Dictionary of headers

    Returns:
        Tuple of (media_type, parameters)
    """
    content_type = headers.get("content-type", "")
    if not content_type:
        return "", {}

    parts = content_type.split(";")
    media_type = parts[0].strip().lower()

    params = {}
    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip().lower()] = value.strip().strip('"')

    return media_type, params


def is_chunked(headers: Dict[str, str]) -> bool:
    """
    Check if Transfer-Encoding is chunked.

    Args:
        headers: Dictionary of headers

    Returns:
        True if chunked encoding is used
    """
    transfer_encoding = headers.get("transfer-encoding", "").lower()
    return "chunked" in transfer_encoding


def is_connection_keep_alive(headers: Dict[str, str], http_version: str) -> bool:
    """
    Check if connection should be kept alive.

    Args:
        headers: Dictionary of headers
        http_version: HTTP version string (e.g., 'HTTP/1.1')

    Returns:
        True if connection should be kept alive
    """
    connection = headers.get("connection", "").lower()

    if connection == "close":
        return False

    if connection == "keep-alive":
        return True

    # Default behavior depends on HTTP version
    return http_version.decode() >= "HTTP/1.1"


def get_hostname_and_port(host_header: str, is_secure: bool = False) -> Tuple[str, int]:
    """
    Parse Host header into hostname and port.

    Args:
        host_header: Host header value
        is_secure: Whether connection is secure (HTTPS)

    Returns:
        Tuple of (hostname, port)
    """
    default_port = 443 if is_secure else 80

    if not host_header:
        return "", default_port

    if ":" in host_header:
        hostname, port_str = host_header.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            port = default_port
    else:
        hostname = host_header
        port = default_port

    return hostname, port


def get_socket_options(backlog: int = 128) -> List[Tuple[int, int, int]]:
    """
    Get socket options for HTTP server.

    Args:
        backlog: Connection backlog size

    Returns:
        List of socket options
    """
    return [
        (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    ]


def get_client_addr(scope: WWWScope) -> str:
    client = scope.get("client")
    if not client:
        return ""
    return "%s:%d" % client


def get_path_with_query_string(scope: WWWScope) -> str:
    path_with_query_string = urllib.parse.quote(scope["path"])
    if scope["query_string"]:
        # Handle both bytes and string query_string for robustness
        query_string = scope["query_string"]
        if isinstance(query_string, bytes):
            query_string = query_string.decode("ascii")
        path_with_query_string = "{}?{}".format(path_with_query_string, query_string)
    return path_with_query_string
