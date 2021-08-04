import urllib.parse

from app import irbox

from flask import Blueprint
from flask import render_template

remote_blueprint = Blueprint('remote_blueprint', __name__)

@remote_blueprint.route('/remote/<remote_id>')
def remote(remote_id):
    """
    Return remote page.
    """

    safe_remote_id = urllib.parse.quote(remote_id)
    return render_template(f'remotes/{safe_remote_id}.html')
