"""
norx command endpoints.
"""

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app import irbox

from irbox.errors import IrboxError

norx_blueprint = Blueprint('norx_blueprint', __name__)

@norx_blueprint.route('/norx')
def norx():
    """
    norx command.
    """

    try:
        success = irbox.norx()
        message = irbox.response
    except IrboxError as irbox_error:
        success = False
        message = irbox_error.message

    return redirect(url_for(
        'norx_blueprint.norx_success' if success else 'norx_blueprint.norx_failure',
        m = message
    ))

@norx_blueprint.route('/norx/success')
def norx_success():
    """
    Successful norx.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                "norx.html",
                success=True,
                message=message
            )
    )
    response.headers.set('Irbox-Success', 'true')
    return response

@norx_blueprint.route('/norx/failure')
def norx_failure():
    """
    Failed norx.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                "norx.html",
                success=False,
                message=message
            )
    )
    response.headers.set('Irbox-Success', 'false')
    return response
