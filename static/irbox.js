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
});

/*
 * Sends a nop command to the IR box.
 */
function nop() {
  _request('/nop');
}

/*
 * Sends a tx command to the IR box.
 *
 * Args:
 *     args (array of key(str)-value(str) pairs): tx() arguments.
 */
function tx(args) {
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
    _responseContainer.style.display = 'block';
    _responseClose.style.display = _responseContainer.style.display;
  } else {
    _responseContainer.style.display = 'none';
    _responseClose.style.display = _responseContainer.style.display;
  }
}

/*
 * Performs an asynchronous GET request. Updates the status "LED" to indicate
 * progress.
 *
 * Args:
 *     uri (str): The URI with GET parameters to request.
 *     cooldown (int?): Value to pass to _statusColor().
 */
function _request(uri, cooldown = 1000) {
  var request = new XMLHttpRequest();

  request.open('GET', uri, true);

  request.onload = function(e) {
    if (request.readyState === 4) {
      if (request.status === 200) {
        if (request.getResponseHeader('Transmit-Succeeded') === 'true') {
          _statusColor('#080', 2500);
        } else {
          _statusColor('#800');
        }

        _responseContainer.srcdoc = request.responseText;
      } else {
        console.error(request.statusText);
        _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);
        _statusColor('#800');
      }
    }
  };

  request.onerror = function(e) {
    console.error(request.statusText);
    _responseContainer.src = '/error?m=' + encodeURIComponent(request.statusText);
    _statusColor('#800');
  };

  request.send(null);
  _statusColor('#880');
}

/*
 * Sets the status "LED" color.
 *
 * Args:
 *     color (str): The color to set.
 *     cooldown (int?): A delay, in milliseconds, to wait before "cooling down"
 *         to the default "LED" color. Never cools down if non-integer.
 */
function _statusColor(color, cooldown = false) {
  if (!_statusContainer) return;
  _statusContainer.style.backgroundColor = color;

  if (Number.isInteger(cooldown))
    setTimeout(_statusColor, cooldown, _statusDefaultBackgroundColor);
}
