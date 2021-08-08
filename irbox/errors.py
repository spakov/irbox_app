"""
Exception classes.
"""

class IrboxError(Exception):
    """
    Base class for all IR box exceptions. Optionally wraps another exception.

    Attributes:
        base (Exception): Optional. Exception that led to creation of this
            exception.
        message (str): Exception message.
    """

    def __init__(self, base = None):
        """
        Constructor.
        """

        # Note base exception
        self.base = base

        # Set message from base exception
        try:
            self.message = base.message
        except AttributeError:
            self.message = None

        # Update message if possible
        if type(self.base) is TimeoutError:
            self.message = 'Timeout'
        elif type(self.base) is PermissionError:
            self.message = 'Permission denied'
        elif type(self.base) is ConnectionRefusedError:
            self.message = 'Connection refused'

class MalformedArgumentsError(IrboxError):
    """
    Raised when IR box command arguments are malformed.
    """

    def __init__(self):
        """
        Constructor.
        """

        self.message = 'Malformed arguments'
