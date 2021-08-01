from flask import render_template
from flask import request

@app.route('/error')
def error():
    """
    Generic error page.
    """

    message = request.args.get('m')

    return render_template(
            "error.html",
            message=message
    );
