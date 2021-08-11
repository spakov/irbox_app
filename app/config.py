"""
Default IR box configuration. Override this with a `.cfg` file and the
`IRBOX_CONFIG` environment variable!
"""

class DefaultConfig():
    #pylint: disable=too-few-public-methods

    """
    Encapsulates default configuration.
    """

    SECRET_KEY = 'changeme'
    """
    Flask session secret key. Generate these using the guidance outlined at
    https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions.
    """

    HOST_ADDRESS = '0.0.0.0'
    """
    IP address or hostname of the IR box device.
    """

    HOST_PORT = 333
    """
    TCP port number to connect to the IR box device.
    """

    REMOTES = { 'demo': 'Demo Remote' }
    """
    Dictionary of remotes. Keys are the remote ID and values are the name of
    the remote.
    """
