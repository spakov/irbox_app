"""
Flask app.
"""

import logging

from flask import Flask

from irbox.errors import IrboxError

from app import irbox
from app.error import error_blueprint
from app.index import index_blueprint
from app.invalid import invalid_blueprint
from app.nop import nop_blueprint
from app.norx import norx_blueprint
from app.remote import remote_blueprint
from app.rx import rx_blueprint
from app.status import status_blueprint
from app.tx import tx_blueprint

logger = logging.getLogger(__name__)

# Initialize application
app = Flask(__name__)

# Load default configuration
app.config.from_object('app.config.DefaultConfig')

# Load runtime configuration
try:
    app.config.from_envvar('IRBOX_CONFIG')
except RuntimeError:
    logger.warning(
            '[1;31mWARNING[0m: The IRBOX_CONFIG environment variable is '
            'not set. Proceeding with default configuration. Do not expect '
            'this to work well!'
    )

# Enable block trimming to produce nicer HTML
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Register blueprints
app.register_blueprint(error_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(invalid_blueprint)
app.register_blueprint(nop_blueprint)
app.register_blueprint(norx_blueprint)
app.register_blueprint(remote_blueprint)
app.register_blueprint(rx_blueprint)
app.register_blueprint(status_blueprint)
app.register_blueprint(tx_blueprint)

@app.before_first_request
def init():
    """
    Start connection to the IR box immediately before the first request.
    """

    # We don't care about errors right now since we're only doing a soft
    # connect. It's up to each routine that communicates with the IR box from
    # here on out to handle them, though.
    try:
        irbox.connect(app.config['HOST_ADDRESS'], app.config['HOST_PORT'], True)
    except IrboxError:
        pass

# Kick off Flask in debug mode
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='5000', extra_files=['irbox.cfg'], debug=True)
