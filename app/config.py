"""
Default IR box configuration. Override this with a `.cfg` file named in the
`IRBOX_CONFIG` environment variable!
"""

class DefaultConfig():
    # pylint: disable=too-few-public-methods

    """
    Encapsulates default configuration.
    """

    HOST_ADDRESS: str = '0.0.0.0'
    """
    IP address or hostname of the IR box device.
    """

    HOST_PORT: int = 333
    """
    TCP port number to connect to the IR box device.
    """

    RETRY: bool = False
    """
    Whether or not to attempt reconnection after a response timeout. Can be
    useful for flaky connections.
    """

    REMOTES: dict = { 'demo': 'Demo Remote' }
    """
    Dictionary of remotes. Keys are the remote ID and values are the name of
    the remote.
    """
