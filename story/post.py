import flask

from chainstories import db
from flask.ext.login import current_user
from story.models import Story
from snippet.models import Snippet

def machine(request):
    if not current_user.is_authenticated():
        return { "error": "User is not authenticated." }

    if "snippet_id" not in request.form:
        return { "error": "Missing parameters." }

    snippet_obj = Snippet.query.get(request.form["snippet_id"])

    if not snippet_obj:
        return { "error": "Could not find specified snippet." }

    story_obj = Story(current_user, snippet_obj)
    db.session.add(story_obj)
    db.session.commit()

    return { "data": {
        "id": story_obj.id,
        "text": story_obj.text,
        "snippets": { "href": "/story/%s/snippets" % story_obj.id }
    } }


def human(request):
    result = machine(request)
    
    if "error" in result:
        flask.flash(result["error"])
        return flask.redirect("/home")

    flask.flash(story.CREATED_MESSAGE)
    return flask.redirect("/story/%s" % result["id"])
