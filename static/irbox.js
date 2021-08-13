/*
 * Routines used to communicate with the IR box.
 */

/* Do some housekeeping after the DOM is built */
document.addEventListener('DOMContentLoaded', function() {
  /* The status "LED" */
  window._statusContainer = document.getElementById('status');

  /* The default color the status "LED" */
  if (_statusContainer !== null) {
    window._statusDefaultBackgroundColor = _statusContainer.style.backgroundColor;
  }

  /* The response container */
  window._responseContainer = document.getElementById('response');

  /* The response close button */
  window._responseClose = document.getElementById('response-close');

  /* Status "LED" busy color */
  window._statusBusyColor = '#880';

  /* Status "LED" success color */
  window._statusSuccessColor = '#080';

  /* Status "LED" failure color */
  window._statusFailureColor = '#800';

  /* Status "LED" generic response color */
  window._statusGenericColor = '#fff';

  /* Status "LED" cooldown */
  window._statusCooldown = 250;

  /* The last timeout for callbacks */
  window._timeout = null;

  /* The Start button */
  window._start = document.getElementById('start');

  /* The Stop button */
  window._stop = document.getElementById('stop');

  /* Call any post-load routines that are defined. Guarantees that global
   * variables will exist when this is called. */
  if (typeof afterLoad === 'function') afterLoad();
});

/*
 * Sends a nop command to the IR box.
 */
function nop() {
  _request('/nop');
}

/*
 * Sends a tx command to the IR box.
 */
function tx(args) {
  /* If arguments are integers, convert them to hex strings */
  for (var key in args) {
    if (Number.isInteger(args[key])) args[key] = '0x' + args[key].toString(16);
  }

  _request('/tx?' + new URLSearchParams(args));
}

/*
 * Sends an rx command to the IR box.
 */
function rx() {
  _responseContainer.contentWindow.rxMessages();
  _request('/rx', 1);
}

/*
 * Sends a norx command to the IR box.
 */
function norx() {
  _request('/norx', 2);
  _responseContainer.contentWindow.rxMessages(false);
}

/*
 * Sends an invalid command to the IR box (for debugging purposes).
 */
function invalid() {
  _request('/invalid');
}

/*
 * Processes received messages, for receive mode.
 *
 * Args:
 *     start (bool): Start if true, stop if false.
 */
function rxMessages(start = true) {
  if (start) {
    /* Call me again in one second */
    _timeout = setTimeout(rxMessages, 250);

    /* Request a message */
    _request('/rx/message', 3);
  } else {
    /* Cancel timeout */
    clearTimeout(_timeout);
    _timeout = null;
  }
}

/*
 * Toggles visibility of the response container.
 */
function toggleResponse() {
  if (window.getComputedStyle(_responseContainer, null).getPropertyValue('display') === 'none') {
    showResponse();
  } else {
    showResponse(false);
  }
}

/*
 * Shows or hides the response container and response close button.
 *
 * Args:
 *     visible (bool): Whether or not to display the response container and
 *         response close button.
 */
function showResponse(visible = true) {
  /* Modify response container visibility */
  _responseContainer.style.display = (visible ? 'block' : 'none');
  _responseClose.style.display = _responseContainer.style.display;
}

/*
 * Toggles alternate alignment.
 */
function toggleAlt() {
  _toggleAltElement(document.getElementById('back'));
  _toggleAltElement(document.getElementById('alt-toggle'));
  _toggleAltElement(document.getElementById('response'));
  _toggleAltElement(document.getElementById('response-close'));
  _toggleAltElement(document.getElementById('remote'), true);

  /* Save preference as cookie */
  const expires = new Date();
  expires.setTime(expires.getTime() + 365 * 24 * 60 * 60 * 1000);
  document.cookie = (
    'alt-align='
    + _getAltState()
    + '; SameSite=Strict; expires='
    + expires.toUTCString()
    + '; path=/'
  );
}

/*
 * Toggles alternate alignment of a single element.
 *
 * Args:
 *     element (Object): The element of which to modify alignment.
 *     recurse (bool): Whether or not to toggle child elements as well.
 */
function _toggleAltElement(element, recurse = false) {
  /* Ignore bad elements */
  if (!element) return;

  /* Ignore elements with no-alt class */
  if (element.className.search(/no-alt/) != -1) return;

  /* Elements with alt-align class */
  if (element.className.search(/alt-align/) != -1) {
    /* Remove alt-align class */
    element.className = element.className.replaceAll(/ ?alt-align/g, '')
  /* Elements without alt-align class */
  } else {
    /* Toggle alt-align class */
    if (element.className.length == 0) {
      element.className = 'alt-align'
    } else {
      element.className += ' alt-align'
    }
  }

  if (recurse) {
    /* Call recursively for children */
    for (var i = 0; i < element.children.length; i++) {
      _toggleAltElement(element.children[i], true);
    }
  }
}

/*
 * Gets the alternate alignment state. Returns true if the alt-align class
 * exists in the alt-toggle container or false otherwise.
 */
function _getAltState() {
  if (!document.getElementById('alt-toggle')) return;

  if (document.getElementById('alt-toggle').className.search(/alt-align/) != -1) {
    return true;
  }

  return false;
}

/*
 * Performs an asynchronous GET request. Updates the status "LED" to indicate
 * progress.
 *
 * Args:
 *     uri (str): The URI with GET parameters to request.
 *     receiveMode (int): Receive mode stage. 0 to disable (for normal
 *         requests), 1 for an outer rx (Start), 2 for an outer norx (Stop),
 *         and 3 for the second stage (inner).
 */
function _request(uri, receiveMode = 0) {
  var request = new XMLHttpRequest();

  /* Set up request */
  request.open('GET', uri, true);

  /* Called when request performs an action */
  request.onload = function(e) {
    /* Request completed */
    if (request.readyState === 4) {
      /* HTTP 200 */
      if (request.status === 200) {
        /* Either no receive mode, or all receive modes except inner page */
        if (receiveMode < 3) {
          /* Receive mode */
          if (receiveMode > 0) _statusColor(_statusGenericColor);

          /* Receive mode Start button */
          if (receiveMode === 1) {
            /* Disable Start button, enable Stop button */
            _start.attributes.setNamedItem(document.createAttribute('disabled'));
            _stop.attributes.removeNamedItem('disabled');
          /* Receive mode Stop button */
          } else if (receiveMode === 2) {
            /* Disable Stop button, enable Start button */
            _start.attributes.removeNamedItem('disabled');
            _stop.attributes.setNamedItem(document.createAttribute('disabled'));
          /* Successful request, not receive mode */
          } else if (request.getResponseHeader('Irbox-Success') === 'true') {
            /* Success status */
            _statusColor(_statusSuccessColor);
          /* Failed request, not receive mode */
          } else {
            /* Failure status */
            _statusColor(_statusFailureColor);
          }

          /* Not receive mode */
          if (receiveMode === 0) {
            /* Update response */
            _responseContainer.srcdoc = request.responseText;
          }
        /* Receive mode, inner page */
        } else {
          messages = document.getElementById('messages')

          if (messages) {
            /* Ignore empty messages */
            if (request.responseText !== '') {
              /* Log message */
              messages.innerHTML += (
                '<li><span class="message">'
                + _formatMessage(request.responseText)
                + '</span></li>'
              );
            }
          }
        }
      /* HTTP other than 200 */
      } else {
        /* Log error */
        console.error(request.statusText);

        /* Not receive mode */
        if (receiveMode === 0) {
          /* Update response */
          _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);

          /* Failure status */
          _statusColor(_statusFailureColor);
        }
      }
    }
  };

  /* No receive mode, or all receive modes except inner page */
  if (receiveMode < 3) {
    /* Error callback */
    request.onerror = function(e) {
      /* Log error */
      console.error(request.statusText);

      /* Update response */
      _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);

      /* Failure status */
      _statusColor(_statusFailureColor);
    };
  /* Receive mode, inner page */
  } else {
    /* Error callback */
    request.onerror = function(e) {
      /* Log error */
      console.error(request.statusText);
    };
  }

  /* Make the request */
  request.send(null);

  /* No receive mode, or all receive modes except inner page: busy status */
  if (receiveMode < 3) _statusColor(_statusBusyColor);
}

/*
 * Formats a message for display. Handles oddly formatted commands, even beyond
 * what the IR box returns.
 */
function _formatMessage(message) {
  /* Start with just the message */
  var startTags = '';
  var formattedMessage = message;
  var endTags = '';

  /* Assume valid command */
  var valid = true;

  /* Check for tx command */
  if (message.startsWith('+tx')) {
    /* Put raw command in title attribute */
    startTags = '<span title="' + message + '">'
    endTags = '</span>'

    /* Remove parentheses */
    message = message.replace(/\+tx *\(/, '');
    message = message.replace(/\)/, '');

    /* Get arguments */
    args = message.split(',');

    /* Check for valid number of arguments */
    if (args.length < 3 || args.length > 5) valid = false;

    /* Loop through all arguments */
    if (valid) for (var i = 0; i < args.length; i++) {
      /* Trim */
      args[i] = args[i].trim();

      /* Check for decimal value */
      if (Number.isInteger(args[i])) {
        /* Assume decimal, so convert to hex */
        args[i] = args[i].toString(16);
      }
    }

    /* The first three arguments are protocol, address, and command, which all
     * protocols use */
    if (valid) {
      var protocol = args[0];
      var address = args[1];
      var command = args[2];
    }

    /* Set index to point to next argument */
    index = 3;

    /* By default, no bits or repeats */
    var bits = false;
    var repeats = false;

    /* Check for Sony protocol */
    if (valid && protocol == '0x13') {
      /* We need at least one more argument */
      if (args.length < 4) valid = false;

      /* Next argument is bits */
      if (valid) bits = args[3];

      /* Start at next argument */
      index++;
    }

    /* Process repeats */
    if (valid && index < args.length) repeats = args[index];

    /* Add commas as needed */
    if (valid) {
      protocol += ',';
      command += ',';
      if (args.length > 3) address += ',';
      if (args.length > 4 && bits) bits += ',';
    }

    /* Build command */
    if (valid) formattedMessage = (
      '<span class="brace">{</span> '
      + '<span class="string">\'p\'</span>: '
      + protocol.padEnd(6, ' ')
      + '<wbr>'
      + '<span class="string">\'a\'</span>: '
      + address.padEnd(8, ' ')
      + '<wbr>'
      + '<span class="string">\'c\'</span>: '
      + command.padEnd(8, ' ')
      + '<wbr>'
    );

    /* If bits, add those */
    if (valid && bits) formattedMessage += (
      '<span class="string">\'b\'</span>: '
      + bits.padEnd(6, ' ')
      + '<wbr>'
    );

    /* If repeats, add those */
    if (valid && repeats) formattedMessage += (
      '<span class="string">\'r\'</span>: '
      + repeats.padEnd(6, ' ')
      + '<wbr>'
    );

    /* Finish the command */
    if (valid) formattedMessage += '<span class="brace">}</span>';
  }

  /* Check for invalid command */
  if (!valid) {
    startTags = '<span class="negative">';
    formattedMessage = 'Malformed arguments';
    endTags = '</span>';
  }

  /* Check for positive status */
  if (message.startsWith('+')) {
    startTags = '<span class="positive">';
    endTags = '</span>';
  }

  /* Check for negative status */
  if (message.startsWith('-')) {
    startTags = '<span class="negative">';
    endTags = '</span>';
  }

  return startTags + formattedMessage + endTags;
}

/*
 * Sets the status "LED" color.
 *
 * Args:
 *     color (str): The color to set.
 *     cooldown (bool): Mask for _statusCooldown. Set to false to never cool
 *         down and to true to observe _statusCooldown. Exists to prevent
 *         recursive calls from setting an infinite chain of timeouts.
 */
function _statusColor(color, cooldown = true) {
  if (!_statusContainer) return;
  _statusContainer.style.backgroundColor = color;

  if (cooldown && Number.isInteger(_statusCooldown))
    /* If there's an existing timeout, cancel it */
    if (_timeout) {
      clearTimeout(_timeout);
      _timeout = null;
    }

    /* Set a timeout to clear the "LED" */
    _timeout = setTimeout(_statusColor, _statusCooldown, _statusDefaultBackgroundColor, false);
}
