import flask
import accesstoken

from chainstories import db
from accesstoken.models import AccessToken
from flask.ext.login import current_user

def machine(request):
    # Delete all user's tokens.
    deleted = AccessToken.query.filter_by(user = current_user).delete()
    db.session.commit()
    return { "success": "Deleted %s tokens." % deleted }

def human(request):
    result = machine(request)
    flask.flash(accesstoken.LOGGED_OUT)
    return flask.redirect("/home")
