"""
Remote endpoints.
"""

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from app.include import IncludeType
from app.include import remote_include

remote_blueprint = Blueprint('remote_blueprint', __name__)

@remote_blueprint.route('/remote/<remote_id>')
def remote(remote_id):
    """
    Return remote page.
    """

    # Make sure the remote HTML file exists
    remote_html = remote_include(remote_id, IncludeType.HTML)
    if remote_html is None:
        return redirect(url_for(
            'error_blueprint.error',
            m = 'Remote does not exist'
        ))

    # Get remote script and CSS
    remote_script = remote_include(remote_id, IncludeType.SCRIPT)
    remote_css = remote_include(remote_id, IncludeType.CSS)

    return render_template(
            remote_html,
            alt_align=(request.cookies.get('alt-align') == 'true'),
            remote_name=current_app.config['REMOTES'][remote_id],
            remote_script=remote_script,
            remote_css=remote_css
    )
