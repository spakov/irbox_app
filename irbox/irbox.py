"""
Contains class to facilitate communication with the IR box using its protocol.
"""

import logging
import socket
import threading
import time

from irbox.errors import IrboxError
from irbox.errors import MalformedArgumentsError
from irbox.message import Message
from irbox.count_generator import count_generator

logger = logging.getLogger('irbox')

class IrBox:
    # pylint: disable=too-many-instance-attributes

    """
    Class to facilitate communication with the IR box using its protocol.

    Constants:
        _WAIT: Number of seconds to wait each loop when reading data.
        _TIMEOUT: Timeout (in seconds) for connection and to wait for messages
            to be received. Recommend a value no less than 5 to account for
            transmissions with many repeats (e.g., simulating holding a
            button).

    Attributes:
        _socket (socket): TCP socket.
        _reader_thread (Thread): Thread that calls _read().
        _message_count_generator (generator of int): Transmitted message count
            generator.
        _message_count (int): Transmitted message count.
        _messages (list of Message): Received messages, in the order they were
            received.
        _response (str): Last response received from the IR box.
    """

    _WAIT = 0.01
    _TIMEOUT = 5

    def __init__(self, host=None, port=None):
        """
        Constructor. If host and port are specified, connect.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.

        Raises:
            IrboxError: An IR box error.
        """

        # No socket to start
        self._socket = None

        # No reader thread until we do a connect()
        self._reader_thread = None

        # Build generators
        self._message_count_generator = count_generator()
        self._message_count = next(self._message_count_generator)

        # Initialize received messages list
        self._messages = list()

        # No response by default
        self._response = None

        # If host and port were specified, start the connection
        if host and port:
            self.host = host
            self.port = port
            try:
                self.connect(host, port)
            except IrboxError as irbox_error:
                raise irbox_error

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
    def response(self):
        """
        Returns the last response received from the IR box.

        Returns:
            str: The last response received.
        """
        return self._response

    def connect(self, host, port, soft_connect=False):
        """
        Connects to the IR box.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
            soft_connect (bool): Whether or not to perform a "soft connect."
                This means only noting host and port, but saving the actual
                connection for later.

        Raises:
            IrboxError: An IR box error.
        """

        # Note host and port for future _reconnect()
        self.host = host
        self.port = port

        # If this is a "soft connect," don't actually connect now
        if soft_connect:
            self._socket = None
            return

        # Establish TCP socket and configure timeout
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._TIMEOUT)

        # Connect
        try:
            self._socket.connect((host, port))
        except TimeoutError as timeout_error:
            raise IrboxError(timeout_error) from timeout_error
        except socket.timeout as timeout_error:
            raise IrboxError(TimeoutError) from timeout_error
        except PermissionError as permission_error:
            logger.warning('Permission error')
            raise IrboxError(permission_error) from permission_error
        except ConnectionRefusedError as connection_refused_error:
            logger.warning('Connection refused')
            raise IrboxError(connection_refused_error) from connection_refused_error

        # Disable timeout for reading on a separate thread
        self._socket.settimeout(None)

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
            raise TimeoutError

        logger.info('Connected')

    def nop(self):
        """
        Sends a nop command to the IR box. Returns a value indicating whether
        or not the IR box responded positively to the nop command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the nop command.

        Raises:
            IrboxError: An IR box error.
        """

        try:
            return self._send_message('nop')
        except IrboxError as irbox_error:
            raise irbox_error

    def tx(self, args): # pylint: disable=invalid-name
        """
        Sends a tx command to the IR box. Returns a value indicating whether
        or not the IR box responded positively to the tx command.

        Args:
            args (list of str): tx() arguments to join with commas.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the tx command.

        Raises:
            IrboxError: An IR box error.
            MalformedArgumentsError: Unable to parse arguments.
        """

        try:
            message = ','.join(args)
            message = f'tx({message})'
            return self._send_message(message)
        except IrboxError as irbox_error:
            raise irbox_error
        except TypeError as type_error:
            raise MalformedArgumentsError from type_error

    def rx(self): # pylint: disable=invalid-name
        """
        Sends an rx command to the IR box. This puts the IR box in rx mode, to
        be terminated with a norx command. In this mode, the IR box sends tx()
        commands that correspond to IR commands that it receives. To obtain
        those, call get_rx_message() while in rx mode.

        Returns a value indicating whether or not the IR box responded
        positively to the rx command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the tx command.

        Raises:
            IrboxError: An IR box error.
        """

        try:
            return self._send_message('rx')
        except IrboxError as irbox_error:
            raise irbox_error

    def get_rx_message(self):
        """
        Strictly for use in rx mode. Returns a tx() command written by the IR
        box.

        Returns the tx() command read from the IR box, or None if it has not
            written one yet.

        Returns:
            str?: The tx() command read from the IR box, or None if it has not
                written one yet.

        Raises:
            IrboxError: An IR box error.
        """

        try:
            return self._send_message('')
        except IrboxError as irbox_error:
            raise irbox_error

    def norx(self):
        """
        Sends an norx command to the IR box. This exits rx mode.

        Returns a value indicating whether or not the IR box responded
        positively to the norx command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the norx command.

        Raises:
            IrboxError: An IR box error.
        """

        try:
            return self._send_message('norx')
        except IrboxError as irbox_error:
            raise irbox_error

    def invalid(self):
        """
        Sends an invalid command to the IR box (for debugging purposes).
        Returns a value indicating whether or not the IR box responded
        positively to the invalid command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the invalid command.

        Raises:
            IrboxError: An IR box error.
        """

        try:
            return self._send_message('invalid')
        except IrboxError as irbox_error:
            raise irbox_error

    def _close(self):
        """
        Terminates the connection.

        Raises:
            IrboxError: An IR box error.
        """

        # Close socket connections
        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            except OSError as os_error:
                # errno 57 means the socket is already closed, so we only care
                # about other errors
                if os_error.errno != 57:
                    raise IrboxError(os_error) from os_error

            self._socket = None

            # Take the opportunity to clear the messages list and free a bit of
            # memory
            if self._messages is not None:
                self._messages.clear()

            # If called from destructor, logger may no longer exist
            if logger is not None:
                logger.info('Connection closed')

    # TODO: raise exceptions instead of using strings
    def _send_message(self, message):
        """
        Sends a message to the IR box. Use this method to communicate with the
        IR box.

        Args:
            message (str): The message to send. Must contain only ASCII
                characters.
            validate (bool): Whether or not to validate by waiting for a
                positive response (i.e., one that begins with +).

        Returns:
            bool:
                A value indicating whether or not a positive response was
                received (if validate) within _TIMEOUT

        Raises:
            IrboxError: An IR box error.
        """

        # Track message count internally for now
        message_count = next(self._message_count_generator)

        # Build a new message to receive data
        self._messages.append(Message(message_count))

        try:
            self._write(message.encode('ascii'))
        except TimeoutError:
            logger.debug('Message timeout')
            self._response = 'Message timeout'
            return False
        logger.debug('Message(%d): [%s]', message_count, message)

        # Check for a response within _TIMEOUT
        start = time.perf_counter()
        while time.perf_counter() - start < self._TIMEOUT:
            response = self._receive_message(message_count)
            if response is not None:
                # Increment message count atomically
                self._message_count = message_count

                # Return message
                self._response = response
                return response[:1] == '+'

            time.sleep(self._WAIT)

        logger.debug('Response timeout')
        self._response = 'Response timeout'
        return False

    def _receive_message(self, message_id):
        """
        Returns the response corresponding to the message identified by the
        specified message count.

        This is invoked automatically by _send_message() and should not need to
        be called separately.

        Args:
            message_id (int): The ID of the message to obtain a response to.

        Returns:
            str: The message that was received, or None if no message is
                available.
        """

        # Iterate through the list to find the correct message
        message = None
        for _message in self._messages:
            if _message.message_id == message_id and _message.message is not None:
                message = _message

        # Remove this message from the list, if found, and return it
        if message is not None:
            self._messages.remove(message)
            return message.message

        return None

    def _reconnect(self):
        """
        Reconnects to the IR box using the host and port previously passed to
        connect().

        This is a low-level method and not meant to be called directly.

        Raises:
            IrboxError: An IR box error.
        """

        # Close and connect again
        self._close()
        try:
            self.connect(self.host, self.port)
        except IrboxError as irbox_error:
            raise irbox_error

    def _read(self):
        """
        Reads messages from the IR box, one byte at a time. Messages match
        /.*\r\n/. Expects the _messages list to contain one Message object per
        message received. Fills in the message text in the order messages
        appear in the list. Blocks until a full message is received. Meant to
        run forever in its own thread.

        This is a low-level method and not meant to be called directly.

        Raises:
            IrboxError: An IR box error.
        """

        while True:
            message = b''

            # Read messages (any bytes until \r\n)
            while not message.endswith('\r\n'.encode('ascii')):
                if self._socket is None:
                    time.sleep(self._WAIT)
                    break

                try:
                    byte = self._socket.recv(1)
                except TimeoutError:
                    # Socket timed out, so close the connection
                    self._close()
                except OSError as os_error:
                    # errno 57 means the socket is already closed
                    if os_error.errno == 57:
                        byte = b''
                    else:
                        raise IrboxError(os_error) from os_error

                if byte == b'':
                    # Connection closed
                    self._close()
                    break

                message += byte

            # Fill in the first message
            if message != b'':
                self._messages[-1].message = message.decode('ascii')[:-2]
                logger.debug(
                        'Response(%d): [%s].message}]',
                        self._messages[-1].message_id,
                        self._messages[-1].message
                )

    def _write(self, message):
        """
        Sends a message to the IR box.

        This is a low-level method and not meant to be called directly.

        Args:
            message (bytes): The message to send.

        Returns:
            int: The number of bytes written.

        Raises:
            IrboxError: An IR box error.
        """

        sent = 0
        total_sent = 0

        # If message is empty, do nothing
        if message == b'':
            return 0

        # If socket has been destroyed, reestablish first
        if self._socket is None:
            try:
                self._reconnect()
            except IrboxError as irbox_error:
                raise irbox_error

        # Append newline if not present
        if message[:-2] != b'\r\n':
            message += b'\r\n'

        # Send the message
        while total_sent < len(message):
            try:
                sent = self._socket.send(message)
            except TimeoutError as timeout_error:
                raise IrboxError(timeout_error) from timeout_error
            except socket.timeout as socket_timeout:
                raise IrboxError(TimeoutError) from socket_timeout
            except BrokenPipeError:
                try:
                    self._reconnect()
                except TimeoutError as timeout_error:
                    raise IrboxError(timeout_error) from timeout_error

                continue

            if sent == 0:
                return 0

            total_sent += sent
