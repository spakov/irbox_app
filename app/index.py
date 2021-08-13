"""
Index endpoint.
"""

from flask import current_app
from flask import Blueprint
from flask import render_template

from app.include import IncludeType
from app.include import remote_include

index_blueprint = Blueprint('index_blueprint', __name__)

@index_blueprint.route('/')
def index():
    """
    Return index page (remote).
    """

    # Start with no remotes
    remotes = {}

    # Loop through each remote
    for remote_id, remote_name in current_app.config['REMOTES'].items():
        # Get remote URL and image
        remote_url = remote_include(remote_id, IncludeType.URL)
        remote_image = remote_include(remote_id, IncludeType.IMAGE)

        # Build a dictionary of remotes with keys of remote ID and values of a
        # tuple of remote name, remote_url, and remote image
        remotes[remote_id] = (remote_name, remote_url, remote_image)

    return render_template(
            'index.html',
            remotes=remotes
    )
