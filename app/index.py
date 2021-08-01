from flask import render_template

@app.route('/')
def index():
    """
    Return index page (remote).
    """

    return render_template('index.html')
