from app import irbox

from flask import Blueprint
from flask import render_template

index_blueprint = Blueprint('index_blueprint', __name__)

@index_blueprint.route('/')
def index():
    """
    Return index page (remote).
    """

    return render_template('index.html')
