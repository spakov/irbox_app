/*
 * Routines used to communicate with the IR box.
 */

/* Do some housekeeping after the DOM is built */
document.addEventListener("DOMContentLoaded", function() {
  /* The status "LED" */
  window._statusContainer = document.getElementById('status');

  /* The default color the status "LED" */
  window._statusDefaultBackgroundColor = _statusContainer.style.backgroundColor;

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

  /* Status "LED" cooldown */
  window._statusCooldown = 250;

  /* The last timeout for turning off the status "LED" */
  window._timeout = null;
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
 * Sends an invalid command to the IR box (for debugging purposes).
 */
function invalid() {
  _request('/invalid');
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
}

/*
 * Toggles alternate alignment of a single element.
 *
 * Args:
 *     recurse (bool): Whether or not to toggle child elements as well.
 */
function _toggleAltElement(element, recurse = false) {
  if (!element) return;

  if (element.className.search(/alt-align/) != -1) {
    element.className = element.className.replaceAll(/ ?alt-align ?/g, '')
  } else if (element.className.search(/no-alt/) == -1) {
    if (element.className.length == 0) {
      element.className = 'alt-align'
    } else {
      element.className += ' alt-align'
    }
  }

  if (recurse) {
    for (var i = 0; i < element.children.length; i++) {
      _toggleAltElement(element.children[i], true);
    }
  }
}

/*
 * Performs an asynchronous GET request. Updates the status "LED" to indicate
 * progress.
 *
 * Args:
 *     uri (str): The URI with GET parameters to request.
 */
function _request(uri) {
  var request = new XMLHttpRequest();

  request.open('GET', uri, true);

  request.onload = function(e) {
    if (request.readyState === 4) {
      if (request.status === 200) {
        if (request.getResponseHeader('Irbox-Success') === 'true') {
          _statusColor(_statusSuccessColor);
        } else {
          _statusColor(_statusFailureColor);
        }

        _responseContainer.srcdoc = request.responseText;
      } else {
        console.error(request.statusText);
        _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);
        _statusColor(_statusFailureColor);
      }
    }
  };

  request.onerror = function(e) {
    console.error(request.statusText);
    _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);
    _statusColor(_statusFailureColor);
  };

  request.send(null);
  _statusColor(_statusBusyColor);
}

/*
 * Sets the status "LED" color.
 *
 * Args:
 *     color (str): The color to set.
 *     cooldown (bool): Mask for _statusCooldown. Set to false to never cool
 *         down and to true to observe _statusCooldown. Exists to prevent
 *         recursive calls from setting timeouts forever.
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
