"""
invalid command endpoints.
"""

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app import irbox

from irbox.errors import IrboxError

invalid_blueprint = Blueprint('invalid_blueprint', __name__)

@invalid_blueprint.route('/invalid')
def invalid():
    """
    Invalid command (for debugging purposes).
    """

    try:
        if irbox.invalid():
            endpoint = 'invalid_blueprint.invalid_success'
            message = None
        else:
            endpoint = 'invalid_blueprint.invalid_failure'
            message = irbox.response
    except IrboxError as irbox_error:
        message = irbox_error.message

    return redirect(url_for(
            endpoint,
            m=message
    ))

@invalid_blueprint.route('/invalid/success')
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
    )
    response.headers.set('Irbox-Success', 'true')
    return response

@invalid_blueprint.route('/invalid/failure')
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
    )
    response.headers.set('Irbox-Success', 'false')
    return response
