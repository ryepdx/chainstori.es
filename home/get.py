import flask
from flask.ext.login import current_user

def machine(request):
    return {"logged_in": current_user.is_authenticated() }

def human(request):
    return flask.render_template("home.html", **machine(request))
