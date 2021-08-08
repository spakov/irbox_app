from app import irbox

from irbox.errors import IrboxError

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

rx_blueprint = Blueprint('rx_blueprint', __name__)

@rx_blueprint.route('/rx')
def rx():
    """
    rx command.
    """

    try:
        success = irbox.rx()
        message = irbox.response
    except IrboxError as irbox_error:
        success = False
        message = irbox_error.message

    return redirect(url_for(
        'rx_blueprint.rx_success' if success else 'rx_blueprint.rx_failure',
        m = message
    ))

@rx_blueprint.route('/rx/success')
def rx_success():
    """
    Successful rx.
    """

    response = make_response(
            render_template(
                "rx-messages.html",
                success=True
            )
    );
    response.headers.set('Irbox-Success', 'true');
    return response;

@rx_blueprint.route('/rx/failure')
def rx_failure():
    """
    Failed rx.
    """

    response = make_response(
            render_template(
                "rx-failure.html",
                success=False
            )
    );
    response.headers.set('Irbox-Success', 'false');
    return response;

@rx_blueprint.route('/rx/viewer')
def rx_viewer():
    """
    rx outer page.
    """

    return render_template("rx.html");

@rx_blueprint.route('/rx/messages')
def rx_messages():
    """
    rx inner page.
    """

    return render_template("rx-messages.html");

@rx_blueprint.route('/rx/message')
def rx_message():
    """
    Raw message text returns from the IR box.
    """

    # Request a message
    irbox.getRxMessage()

    # Build plain-text response
    irbox_response = irbox.response

    # Ignore response timeouts
    if (irbox.response == 'Response timeout'):
        irbox_response = ''

    # Ignore rx (these can slip through due to timing race conditions)
    if (irbox.response == '+rx'):
        irbox_response = ''

    # Ignore norx (these can possibly slip through due to timing race
    # conditions)
    if (irbox.response == '+norx'):
        irbox_response = ''

    # Build response
    response = make_response(irbox_response, 200)
    response.mimetype = 'text/plain'

    return response;
