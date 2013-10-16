import flask
import user.models
import accesstoken
from flask.ext.login import login_user

def machine(request):
    user_obj = user.models.User.query.filter_by(
        username=request.form['username']
    ).first()

    # User not found?
    if (not user_obj or not user_obj.check_password(request.form['password'])):
        return { "error": "Invalid username or password!" }

    # Create an access token for this user if they don't have one.
    if not user_obj.access_tokens:
        accesstoken.create_for(user_obj)

    # Login the user.
    login_user(user_obj)

    return {
        "success": accesstoken.LOGGED_IN,
        "data": { "token": user_obj.get_auth_token() }
    }

def human(request):
    result = machine(request)
    flask.flash(result['error'] if 'error' in result else result['success'])
    return flask.redirect("/home")
