"""
Include helper routines.
"""

import logging
import os
import re
import urllib.parse

from enum import Enum, auto

from flask import url_for

logger = logging.getLogger(__name__)

class IncludeType(Enum):
    """
    Remote include types.
    """

    HTML = auto()
    """
    Generate an HTML include.
    """

    URL = auto()
    """
    Generate a URL include.
    """

    SCRIPT = auto()
    """
    Generate a script include.
    """

    CSS = auto()
    """
    Generate a CSS include.
    """

    IMAGE = auto()
    """
    Generate an image include.
    """


def check_safety(remote_id):
    """
    Prints a warning if a remote ID contains illegal characters. The warning
    includes the unsafe remote ID and the equivalent safe file name.

    Args:
        remote_id (str): The remote ID for which to check safety
    """

    _safe_remote_id = safe_remote_id(remote_id)

    if _safe_remote_id != remote_id:
        logger.warning(
                "Potentially unsafe remote ID `%s' will be referenced as `%s' "
                'instead.',
                remote_id,
                _safe_remote_id
        )

def remote_include(remote_id, include_type):
    """
    Returns the safe file path to a specified include type for a given remote
    ID.

    Args:
        remote_id (str): The remote ID to build include for
        include_type (IncludeType): The include type to build a path for

    Returns:
        str: Safe file path to a specified include type for a given remote ID,
            or `None` if the file does not exist.
    """

    def missing_html_warning(remote_id, path):
        """
        Issues a missing HTML file warning.

        Args:
            remote_id (str): The remote ID to issue the warning about
            path (str): The path at which the HTML was expected
        """

        # Issue a warning
        logger.warning(
                "Remote `%s' has no valid HTML file associated with it! "
                "Expected to find HTML at `%s'.",
                remote_id,
                path
        )

    # Templates directory
    TEMPLATES = 'templates' # pylint: disable=invalid-name

    # All paths include remotes
    path = 'remotes'

    # By default, use html as extension
    extension = 'html'

    # HTML is handled differently than the rest
    if include_type == IncludeType.HTML:
        # Build safe path
        safe_path = safe_file_path(path, remote_id, extension)

        # Check for existence
        if is_file(f'{TEMPLATES}/{safe_path}'):
            return safe_path

        # Issue a warning
        missing_html_warning(remote_id, safe_path)

        return None

    # URL is handled differently than the rest
    if include_type == IncludeType.URL:
        # Build safe path
        safe_path = safe_file_path(f'{TEMPLATES}/{path}', remote_id, extension)

        # Remote endpoint
        REMOTE = 'remote_blueprint.remote' # pylint: disable=invalid-name

        # Check for existence
        if is_file(safe_path):
            return url_for(REMOTE, remote_id=safe_remote_id(remote_id))

        # Issue a warning
        missing_html_warning(remote_id, safe_path)
        logger.warning(
                "Remote `%s' will not be displayed in the index.",
                remote_id
        )

        return None

    # Build path for SCRIPT, CSS, or IMAGE
    if include_type == IncludeType.SCRIPT:
        path += '/scripts'
        extension = 'js'
    elif include_type == IncludeType.CSS:
        path += '/css'
        extension = 'css'
    elif include_type == IncludeType.IMAGE:
        path += '/images'
        extension = 'png'

    # Build safe path
    safe_path = safe_file_path(path, remote_id, extension)

    # Static directory
    STATIC = 'static' # pylint: disable=invalid-name

    # Check for existence
    if is_file(f'{STATIC}/{safe_path}'):
        return url_for(STATIC, filename=safe_path)

    return None

def safe_remote_id(remote_id):
    """
    Returns safe remote ID generated from the remote ID that cannot contain any
    illegal characters, for both a file name and for a URL.

    Args:
        remote_id (str): The remote ID to convert to a safe file name

    Returns:
        str: Safe remote ID that cannot contain any illegal characters.
    """

    # Return URL-safe string, with unsafe characters replaced with _
    return re.sub(
            r'[^A-Za-z0-9._-]',
            '_',
            urllib.parse.quote(remote_id)
    )

def safe_file_path(path, remote_id, extension):
    """
    Returns specified path prepended to safe file name generated from the
    remote ID that cannot contain any illegal characters, for both a file name
    and for a URL. Appends period and extension.

    Assumes `path` and `extension` are safe already (i.e., not based on user
    input).

    The safe file name cannot contain any slashes, meaning it is guaranteed to
    be within `path`.

    Args:
        path (str): The path of the directory that contains the file
        remote_id (str): The remote ID to convert to a safe file name

    Returns:
        str: Safe file path and name that cannot contain any illegal characters
            and is guaranteed to refer to a file within `path`, including
            period and extension.
    """

    return (
            f'{path}/'
            + safe_remote_id(remote_id)
            + f'.{extension}'
    )

def is_file(filename):
    """
    Returns a value indicating whether or not a file exists.

    Args:
        filename (str): The name of the file to check

    Returns:
        bool: A value indicating whether or not the file exists.
    """

    return os.path.isfile(filename)
