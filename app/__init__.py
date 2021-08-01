from flask import Flask

from irbox import IrBox

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Create IR box object
irbox = IrBox()

@app.before_first_request
def init():
    """
    Start connection to the IR box immediately before the first request.
    """

    irbox.connect('192.168.0.160', 333)
