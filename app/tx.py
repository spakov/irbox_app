from app import irbox

from irbox.errors import MalformedArgumentsError
from irbox.protocol import Protocol

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

tx_blueprint = Blueprint('tx_blueprint', __name__)

@tx_blueprint.route('/tx')
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
    except TypeError:
        # Malformed arguments
        return redirect(url_for(
                'tx_blueprint.tx_failure',
                m='Malformed arguments',
                p=protocol,
                a=address,
                c=command,
                r=repeats,
                b=bits
        ))
    except ValueError:
        protocol_decimal = Protocol.UNKNOWN.value

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
                'tx_blueprint.tx_failure',
                m='Unsupported protocol',
                p=protocol,
                a=address,
                c=command,
                r=repeats,
                b=bits
        ))

    # Send the tx() command
    try:
        success = irbox.tx(args)
    except MalformedArgumentsError:
        # Arguments are malformed
        return redirect(url_for(
                'tx_blueprint.tx_failure',
                m='Malformed arguments',
                p=protocol,
                a=address,
                c=command,
                r=repeats,
                b=bits
        ))

    if success:
        endpoint = 'tx_blueprint.tx_success'
    else:
        endpoint = 'tx_blueprint.tx_failure'

    message = irbox.response

    return redirect(url_for(
            endpoint,
            m=message,
            p=protocol,
            a=address,
            c=command,
            r=repeats,
            b=bits
    ))

@tx_blueprint.route('/tx/success')
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
    response.headers.set('Irbox-Success', 'true');
    return response;

@tx_blueprint.route('/tx/failure')
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
    response.headers.set('Irbox-Success', 'false');
    return response;
