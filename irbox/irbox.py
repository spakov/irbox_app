"""
Contains class to facilitate communication with the IR box using its protocol.
"""

import logging
import socket
import threading
import time

from irbox.counter import count_generator
from irbox.errors import MalformedArgumentsError
from irbox.message import Message

logger = logging.getLogger(__name__)

class IrBox:
    """
    Class to facilitate communication with the IR box using its protocol.

    Constants:
        _WAIT: Number of seconds to wait each loop when reading data.
        _TIMEOUT: Timeout (in seconds) for connection and to wait for messages
            to be received.

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
    _TIMEOUT = 1

    def __init__(self, host=None, port=None):
        """
        Constructor. If host and port are specified, connect.

        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.

        Raises:
            TimeoutError: Timeout occurred when attempting to establish socket
                connection.
        """

        # No reader thread until we do a connect()
        self._reader_thread = None

        # Build generators
        self._message_count_generator = count_generator();
        self._message_count = next(self._message_count_generator);

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
            except TimeoutError as timeout_error:
                raise timeout_error

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
            TimeoutError: Timeout occurred when attempting to establish socket
                connection.
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
        self._socket.settimeout(self._TIMEOUT);

        # Connect
        try:
            self._socket.connect((host, port))
        except TimeoutError as timeout_error:
            raise timeout_error
        except socket.timeout as timeout_error:
            raise TimeoutError

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

        Raises:
            MalformedArgumentsError: Unable to parse arguments.
        """

        try:
            message = ','.join(args)
            message = f'tx({message})'
            return self._send_message(message)
        except TypeError:
            raise MalformedArgumentsError

    def rx(self):
        """
        Sends an rx command to the IR box. This puts the IR box in rx mode, to
        be terminated with a norx command. In this mode, the IR box sends tx()
        commands that correspond to IR commands that it receives. To obtain
        those, call getRxMessage() while in rx mode.

        Returns a value indicating whether or not the IR box responded
        positively to the rx command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the tx command.
        """

        return self._send_message('rx')
    
    def getRxMessage(self):
        """
        Strictly for use in rx mode. Returns a tx() command written by the IR
        box.

        Returns the tx() command read from the IR box, or None if it has not
            written one yet.

        Returns:
            str?: The tx() command read from the IR box, or None if it has not
                written one yet.
        """

        # TODO: implement me

    def norx(self):
        """
        Sends an norx command to the IR box. This exits rx mode.

        Returns a value indicating whether or not the IR box responded
        positively to the norx command.

        Returns:
            bool: A value indicating whether or not the IR box responded
                positively to the norx command.
        """

        return self._send_message('rx')

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

        # Close socket connections
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

            # Take the opportunity to clear the messages list and free a bit of
            # memory
            if self._messages is not None:
                self._messages.clear()

            # If called from destructor, logger may no longer exist
            if logger is not None:
                logger.info('Connection closed')

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
        """

        # Track message count internally for now
        message_count = next(self._message_count_generator)

        # Build a new message to receive data
        self._messages.append(Message(message_count))

        try:
            self._write(message.encode('ascii'))
        except TimeoutError:
            logger.debug(f'Message timeout')
            self._response = 'Message timeout'
            return False
        logger.debug(f'Message({message_count}): [{message}]')

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

        logger.debug(f'Response timeout')
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
            TimeoutError: Timeout occurred when attempting to establish socket
                connection.
        """

        # Close and connect again
        self._close()
        try:
            self.connect(self.host, self.port)
        except TimeoutError as timeout_error:
            raise timeout_error

    def _read(self):
        """
        Reads messages from the IR box, one byte at a time. Messages match
        /.*\r\n/. Expects the _messages list to contain one Message object per
        message received. Fills in the message text in the order messages
        appear in the list. Blocks until a full message is received. Meant to
        run forever in its own thread.

        This is a low-level method and not meant to be called directly.
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
                        raise os_error

                if byte == b'':
                    # Connection closed
                    self._close()
                    break

                message += byte

            # Fill in the first message
            if message != b'':
                self._messages[-1].message = message.decode('ascii')[:-2]
                logger.debug(f'Response({self._messages[-1].message_id}): [{self._messages[-1].message}]')

    def _write(self, message):
        """
        Sends a message to the IR box.

        This is a low-level method and not meant to be called directly.

        Args:
            message (bytes): The message to send.

        Returns:
            int: The number of bytes written.

        Raises:
            TimeoutError: Timeout occurred when attempting to establish socket
                connection.
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
            except TimeoutError as timeout_error:
                raise timeout_error

        # Append newline if not present
        if message[:-2] != b'\r\n':
            message += b'\r\n'

        # Send the message
        while (total_sent < len(message)):
            try:
                sent = self._socket.send(message)
            except TimeoutError as timeout_error:
                raise timeout_error
            except socket.timeout:
                raise TimeoutError
            except BrokenPipeError:
                try:
                    self._reconnect()
                except TimeoutError as timeout_error:
                    raise timeout_error

                continue

            if (sent == 0):
                return 0

            total_sent += sent
