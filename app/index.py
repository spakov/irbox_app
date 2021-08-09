"""
Index endpoint.
"""

import os

from flask import current_app
from flask import Blueprint
from flask import render_template
from flask import url_for

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
        # Get remote image
        remote_image = f'remotes/images/{remote_id}.png'
        if os.path.isfile(f'static/{remote_image}'):
            remote_image = url_for(
                    'static',
                    filename=remote_image
            )
        else:
            remote_image = None

        # Build a dictionary of remotes with keys of remote ID and values of a
        # tuple of remote name and remote image
        remotes[remote_id] = (remote_name, remote_image)

    return render_template(
            'index.html',
            remotes=remotes
    )
