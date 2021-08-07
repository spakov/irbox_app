from app import irbox

from flask import Blueprint
from flask import render_template
from flask import request

status_blueprint = Blueprint('status_blueprint', __name__)

@status_blueprint.route('/status')
def status():
    """
    Filler page for status iframe.
    """

    return render_template("status.html");
