import flask

def machine(request):
    return {}

def human(request):
    return flask.render_template("home.html", **machine(request))
