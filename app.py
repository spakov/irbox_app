import logging

from flask import Flask

from app import irbox
from app.error import error_blueprint
from app.index import index_blueprint
from app.invalid import invalid_blueprint
from app.nop import nop_blueprint
from app.remote import remote_blueprint
from app.tx import tx_blueprint

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Register blueprints
app.register_blueprint(error_blueprint);
app.register_blueprint(index_blueprint);
app.register_blueprint(invalid_blueprint);
app.register_blueprint(nop_blueprint);
app.register_blueprint(remote_blueprint);
app.register_blueprint(tx_blueprint);

@app.before_first_request
def init():
    """
    Start connection to the IR box immediately before the first request.
    """

    try:
        irbox.connect('192.168.0.160', 333, True)
    except TimeoutError:
        # Nothing to do here except accept that the connection timed out
        pass

# Kick off Flask in debug mode
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='5000', debug=True)
