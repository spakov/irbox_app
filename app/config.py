"""
Default IR box configuration. Override this with a .cfg file and the
IRBOX_CONFIG environment variable!
"""

class DefaultConfig(object):
    """
    Configuration class.

    Constants:
        SECRET_KEY (str): Flask session secret key. Generate these using the
            guidance outlined at
            https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions.
        HOST_ADDRESS (str): IP address or hostname of the IR box device.
        HOST_PORT (int): TCP port number to connect to the IR box device.
        REMOTES (dict of str:str): Dictionary of remotes. Keys are the remote
            ID and values are the name of the remote.
    """

    SECRET_KEY = 'changeme'
    HOST_ADDRESS = '0.0.0.0'
    HOST_PORT = 333
    REMOTES = { 'demo': 'Demo Remote' }
