from app import irbox

from flask import Blueprint
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

nop_blueprint = Blueprint('nop_blueprint', __name__)

@nop_blueprint.route('/nop')
def nop():
    """
    nop command.
    """

    success = irbox.nop()
    message = irbox.response

    return redirect(url_for(
            'nop_blueprint.nop_success' if success else 'nop_blueprint.nop_failure',
            m=message
    ))

@nop_blueprint.route('/nop/success')
def nop_success():
    """
    Successful nop.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "nop.html",
                    success=True,
                    message=message
            )
    );
    response.headers.set('Irbox-Success', 'true');
    return response;

@nop_blueprint.route('/nop/failure')
def nop_failure():
    """
    Failed nop.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "nop.html",
                    success=False,
                    message=message
            )
    );
    response.headers.set('Irbox-Success', 'false');
    return response;
