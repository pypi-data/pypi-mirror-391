"""
Network-related exceptions for the Zephyr server.
"""


class BufferOverflowError(Exception):
    """
    Raised when attempting to write more data to a buffer than its maximum capacity.
    """

    pass
