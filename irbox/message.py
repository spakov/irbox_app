"""
Contains class to facilitate message processing.
"""

class Message:
    """
    Class to facilitate message processing.

    Attributes:
        _message_id (int): Message ID.
        _message (str): Message.
    """

    def __init__(self, message_id):
        """
        Args:
            message_id (int): Message ID.
        """

        self._message_id = message_id
        self._message = None

    @property
    def message_id(self):
        """
        Returns message ID.

        Returns:
            int: Message ID.
        """

        return self._message_id

    @property
    def message(self):
        """
        Returns message.

        Returns:
            str: Message.
        """

        return self._message

    @message.setter
    def message(self, message):
        """
        Sets message.

        Args:
            message (str): Message.
        """

        self._message = message
