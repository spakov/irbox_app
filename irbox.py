import logging
import queue
import socket
import threading
import time

logger = logging.getLogger(__name__)

class IrBox:
    """
    Class to facilitate communication with the IR box using its protocol.

    Constants:
        _WAIT: Number of seconds to wait each loop when reading data.
        _TIMEOUT: Timeout (in seconds) to wait for messages to be received.

    Attributes:
        _socket (socket): TCP socket.
        _messages (list of str): Received message buffer.
        _reader_thread (Thread): Thread that calls _read().
        _error (str): Last error response received.
    """

    _WAIT = 0.1
    _TIMEOUT = 10

    def __init__(self, host=None, port=None):
        """
        Constructor. If host and port are specified, connect.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
        """

        # Initialize received messages queue
        self._messages = queue.SimpleQueue()

        # No reader thread until we do a connect()
        self._reader_thread = None

        # No error message by default
        self._error = None

        # If host and port were specified, start the connection
        if host and port:
            self.host = host
            self.port = port
            self.connect(host, port)

    def __del__(self):
        """
        Destructor. Makes a best-effort attempt to terminate any connection.
        """

        try:
            self._close()
        except AttributeError:
            # Object was probably already destroyed
            pass

    @property
    def error(self):
        """
        Returns the last error response received.

        Returns:
            str: The last error response received.
        """
        return self._error

    def connect(self, host, port):
        """
        Connects to the IR box.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
        """

        # Note host and port for future _reconnect()
        self.host = host
        self.port = port

        # Establish TCP socket and connection
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

        # Start reader thread, if not already running
        if self._reader_thread is None:
            self._reader_thread = threading.Thread(
                    target=self._read,
                    args=(),
                    daemon=True
            )
            self._reader_thread.start()

        # Wait for +
        if not self._send_message(''):
            raise RuntimeError('Connection failed')

        logger.info('Connected')

    def nop(self):
        """
        Sends a nop command to the IR box. Returns a value indicating whether
        or not the IR box responded positively to the nop command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the nop command.
        """

        return self._send_message('nop')

    def tx(self, args):
        """
        Sends a tx command to the IR box. Returns a value indicating whether
        or not the IR box responded positively to the tx command.

        Args:
            args (list of str): tx() arguments to join with commas.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the tx command.
        """

        message = ','.join(args)
        message = f'tx({message})'
        return self._send_message(message)

    def invalid(self):
        """
        Sends an invalid command to the IR box (for debugging purposes).
        Returns a value indicating whether or not the IR box responded
        positively to the invalid command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the invalid command.
        """

        return self._send_message('invalid')

    def _close(self):
        """
        Terminates the connection.
        """

        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            except OSError as os_error:
                # errno 57 means the socket is already closed, so we only care
                # about other errors
                if os_error.errno != 57:
                    raise os_error

            self._socket = None

            # If called from destructor, logger may no longer exist
            if logger is not None:
                logger.info('Connection closed')

    def _receive_message(self):
        """
        Returns the last message received message from the IR box.

        Returns:
            str: The message that was received, or None if no message is
                available.
        """

        if self._messages.empty():
            return None
        message = self._messages.get()
        logger.debug(f'Received: [{message}]')
        return message

    def _send_message(self, message, validate=True):
        """
        Sends a message to the IR box.

        Args:
            message (str): The message to send. Must contain only ASCII
                characters.
            validate (bool): Whether or not to validate by waiting for a
                positive response (i.e., one that begins with +).

        Returns:
            bool:
                If validate = True: A value indicating whether or not a
                    positive response was received (if validate) within
                    _TIMEOUT
                Otherwise: True
        """

        # Send the message
        self._write(message.encode('ascii'))
        logger.debug(f'Sent: [{message}]')

        if validate:
            # Check for a response within _TIMEOUT
            start = time.perf_counter()
            while time.perf_counter() - start < self._TIMEOUT:
                response = self._receive_message()
                if response is not None:
                    if response[:1] == '+':
                        return True
                    else:
                        self._error = response[1:]
                        return False

                time.sleep(self._WAIT)

            self._error = 'Timeout'
            return False

        return True

    def _reconnect(self):
        """
        Reconnects to the IR box using the host and port previously passed to
        connect().

        This is a low-level method and not meant to be called directly.
        """

        # Close and connect again
        self._close()
        self.connect(self.host, self.port)

    def _read(self):
        """
        Reads messages from the IR box, one byte at a time. Messages match
        /.*\r\n/. Adds each message to the _messages queue. Blocks until a full
        message is received. Meant to run forever in its own thread.

        This is a low-level method and not meant to be called directly.
        """

        while True:
            message = b''

            # Read messages (any bytes until \r\n)
            while not message.endswith('\r\n'.encode('ascii')):
                if self._socket is None:
                    time.sleep(self._WAIT)
                    break

                byte = self._socket.recv(1)
                if byte == b'':
                    # Connection closed
                    self._close()
                    break

                message += byte

            # Add to queue
            if message != b'':
                self._messages.put(message.decode('ascii')[:-2])

    def _write(self, message):
        """
        Sends a message to the IR box.

        This is a low-level method and not meant to be called directly.

        Args:
            message (bytes): The message to send.

        Returns:
            int: The number of bytes written.
        """

        # If message is empty, do nothing
        if message == b'':
            return 0

        # If socket has been destroyed, reestablish first
        if self._socket is None:
            self._reconnect()

        # Send the message
        return self._socket.send(message)
