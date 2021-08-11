"""
Status page endpoint.
"""

from flask import Blueprint
from flask import render_template

status_blueprint = Blueprint('status_blueprint', __name__)

@status_blueprint.route('/status')
def status():
    """
    Filler page for status `iframe`.
    """

    return render_template("status.html")
