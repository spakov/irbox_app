import logging

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from irbox import IrBox

from protocol import Protocol

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Create IR box object
irbox = IrBox()

@app.before_first_request
def init():
    """
    Start connection to the IR box immediately before the first request.
    """

    irbox.connect('192.168.0.160', 333)

@app.route('/')
def index():
    """
    Return index page (remote).
    """

    return render_template('index.html')

@app.route('/nop')
def nop():
    """
    nop command.
    """

    return redirect(url_for(
            'nop_success' if irbox.nop() else 'nop_failure'
    ))

@app.route('/nop/success')
def nop_success():
    """
    Successful nop.
    """

    response = make_response(
            render_template(
                    "nop.html",
                    success=True
            )
    );
    response.headers.set('Transmit-Succeeded', 'true');
    return response;

@app.route('/nop/failure')
def nop_failure():
    """
    Failed nop.
    """

    response = make_response(
            render_template(
                    "nop.html",
                    success=False
            )
    );
    response.headers.set('Transmit-Succeeded', 'false');
    return response;

@app.route('/tx')
def tx():
    """
    Transmit command.
    """

    protocol = request.args.get('p')
    address = request.args.get('a')
    command = request.args.get('c')
    repeats = request.args.get('r')
    bits = request.args.get('b')

    # Protocol, address, and command are always required */
    args = [protocol, address, command]

    # Convert protocol to decimal
    try:
        protocol_decimal = int(protocol[2:], 16)
    except ValueError:
        protocol_decimal = 0

    # Build subsequent arguments
    if (
            protocol_decimal == Protocol.NEC.value
            or protocol_decimal == Protocol.APPLE.value
    ):
        # NEC/Apple next argument is repeats (optional)
        if repeats is not None:
            args.append(repeats)
    elif protocol_decimal == Protocol.SONY.value:
        # Sony next argument is bits
        args.append(bits);

        # Then repeats (optional)
        if repeats is not None:
            args.append(repeats)
    else:
        # Protocol is not implemented
        return redirect(url_for(
                'tx_failure',
                m='Unsupported protocol',
                p=protocol,
                a=address,
                c=command,
                r=repeats,
                b=bits
        ))

    if irbox.tx(args):
        endpoint = 'tx_success'
        message = None
    else:
        endpoint = 'tx_failure'
        message = irbox.error

    return redirect(url_for(
            endpoint,
            m=message,
            p=protocol,
            a=address,
            c=command,
            r=repeats,
            b=bits
    ))

@app.route('/tx/success')
def tx_success():
    """
    Successful command transmission.
    """

    message = request.args.get('m')
    protocol = request.args.get('p')
    address = request.args.get('a')
    command = request.args.get('c')
    repeats = request.args.get('r')
    bits = request.args.get('b')

    response = make_response(
            render_template(
                    "tx.html",
                    success=True,
                    message=message,
                    protocol=protocol,
                    address=address,
                    command=command,
                    repeats=repeats,
                    bits=bits
            )
    );
    response.headers.set('Transmit-Succeeded', 'true');
    return response;

@app.route('/tx/failure')
def tx_failure():
    """
    Failed command transmission.
    """

    message = request.args.get('m')
    protocol = request.args.get('p')
    address = request.args.get('a')
    command = request.args.get('c')
    repeats = request.args.get('r')
    bits = request.args.get('b')

    response = make_response(
            render_template(
                    "tx.html",
                    success=False,
                    message=message,
                    protocol=protocol,
                    address=address,
                    command=command,
                    repeats=repeats,
                    bits=bits
            )
    );
    response.headers.set('Transmit-Succeeded', 'false');
    return response;

@app.route('/invalid')
def invalid():
    """
    invalid command. For debugging.
    """

    if irbox.invalid():
        endpoint = 'invalid_success'
        message = None
    else:
        endpoint = 'invalid_failure'
        message = irbox.error

    return redirect(url_for(
            endpoint,
            m=message
    ))

@app.route('/invalid/success')
def invalid_success():
    """
    Successful invalid command. (This should be unreachable.)
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "invalid.html",
                    message=message,
                    success=True
            )
    );
    response.headers.set('Transmit-Succeeded', 'true');
    return response;

@app.route('/invalid/failure')
def invalid_failure():
    """
    Failed invalid command.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "invalid.html",
                    message=message,
                    success=False
            )
    );
    response.headers.set('Transmit-Succeeded', 'false');
    return response;

@app.route('/error')
def error():
    """
    Generic error page.
    """

    message = request.args.get('m')

    return render_template(
            "error.html",
            message=message
    );

# Kick off Flask in debug mode
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='5000', debug=True)
