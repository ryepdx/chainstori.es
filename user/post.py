import flask
import accesstoken
import user
from chainstories import db
from user.models import User
from flask.ext.login import login_user

def machine(request):
    if (not "username" in request.form
    or not "password" in request.form):
        return { "error": "Missing parameters." }

    user_obj = User.query.filter_by(
        username = request.form["username"]).first()
    
    if user_obj:
        return { "error": "Username already taken!" }

    user_obj = User(request.form["username"], request.form["password"])
    db.session.add(user_obj)
    db.session.commit()

    token = accesstoken.create_for(user_obj)
    login_user(user_obj)

    return {
        "success": user.WELCOME_GREETING,
        "data": { "id": user_obj.id, "token": token.token }
    }

def human(request):
    result = machine(request)
    flask.flash(result["error"] if "error" in result else result["success"])
    return flask.redirect("/home")
