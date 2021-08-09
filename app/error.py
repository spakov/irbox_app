"""
Error endpoints.
"""

from flask import Blueprint
from flask import render_template
from flask import request

error_blueprint = Blueprint('error_blueprint', __name__)

@error_blueprint.route('/error')
def error():
    """
    Generic error page.
    """

    message = request.args.get('m')

    return render_template(
            "error.html",
            message=message
    )
