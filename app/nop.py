from flask import make_response
from flask import redirect
from flask import render_template
from flask import url_for

@app.route('/nop')
def nop():
    """
    nop command.
    """

    return redirect(url_for(
            'nop_success' if irbox.nop() else 'nop_failure'
    ))

@app.route('/nop/success')
def nop_success():
    """
    Successful nop.
    """

    response = make_response(
            render_template(
                    "nop.html",
                    success=True
            )
    );
    response.headers.set('Transmit-Succeeded', 'true');
    return response;

@app.route('/nop/failure')
def nop_failure():
    """
    Failed nop.
    """

    response = make_response(
            render_template(
                    "nop.html",
                    success=False
            )
    );
    response.headers.set('Transmit-Succeeded', 'false');
    return response;
