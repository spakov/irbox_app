"""
Remote endpoints.
"""

import os
import urllib.parse

from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import request
from flask import url_for

remote_blueprint = Blueprint('remote_blueprint', __name__)

@remote_blueprint.route('/remote/<remote_id>')
def remote(remote_id):
    """
    Return remote page.
    """

    # Get safe remote ID
    safe_remote_id = urllib.parse.quote(remote_id)

    # Get remote script
    remote_script = f'remotes/scripts/{remote_id}.js'
    if os.path.isfile(f'static/{remote_script}'):
        remote_script = url_for(
                'static',
                filename=remote_script
        )
    else:
        remote_script = None

    # Get remote CSS
    remote_css = f'remotes/css/{remote_id}.css'
    if os.path.isfile(f'static/{remote_css}'):
        remote_css = url_for(
                'static',
                filename=remote_css
        )
    else:
        remote_css = None
    return render_template(
            f'remotes/{safe_remote_id}.html',
            alt_align=(request.cookies.get('alt-align') == 'true'),
            remote_name=current_app.config['REMOTES'][remote_id],
            remote_script=remote_script,
            remote_css=remote_css
    )
