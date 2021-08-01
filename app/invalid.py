from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

@app.route('/invalid')
def invalid():
    """
    invalid command. For debugging.
    """

    if irbox.invalid():
        endpoint = 'invalid_success'
        message = None
    else:
        endpoint = 'invalid_failure'
        message = irbox.error

    return redirect(url_for(
            endpoint,
            m=message
    ))

@app.route('/invalid/success')
def invalid_success():
    """
    Successful invalid command. (This should be unreachable.)
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "invalid.html",
                    message=message,
                    success=True
            )
    );
    response.headers.set('Transmit-Succeeded', 'true');
    return response;

@app.route('/invalid/failure')
def invalid_failure():
    """
    Failed invalid command.
    """

    message = request.args.get('m')

    response = make_response(
            render_template(
                    "invalid.html",
                    message=message,
                    success=False
            )
    );
    response.headers.set('Transmit-Succeeded', 'false');
    return response;
