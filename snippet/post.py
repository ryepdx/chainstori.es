import flask
import snippet
from chainstories import db
from snippet.models import Snippet
from flask.ext.login import login_required, current_user

def machine(request):
    if not current_user.is_authenticated():
        return { "error": "User is not authenticated" }

    if "text" not in request.form:
        return { "error": "Missing parameters." }
    
    parent = Snippet.query.get(request.form.get("parent_id", ""))
    snippet = Snippet(current_user, request.form["text"], parent)
    db.session.add(snippet)
    db.session.commit()

    return { "data": {"id": snippet.id, "text": snippet.text } }


def human(request):
    result = machine(request)

    if "error" in result:
        flask.flash(result["error"])
        return flask.redirect("/home")

    flask.flash(snippet.CREATED_MESSAGE)
    return flask.redirect("/snippet/%s" % result["data"]["id"]) 
