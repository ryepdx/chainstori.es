import flask
from user.models import User
from chainstories import login_manager
from cyborg import DynamicAttributeError

WELCOME_GREETING = "Welcome to chainstori.es!"

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

class UserProfile(object):
    def __init__(self, user_obj):
        self.user = user_obj

    @property
    def get(self):
        return self

    def machine(self, request):
        return { "data": { "username": self.user.username } }

    def human(self, request):
        return flask.render_template(
            "profile.html", **self.machine(request).get("data"))

def __getattr__(username):
    user_obj = User.query.filter_by(username = username).first()

    if user_obj:
        return UserProfile(user_obj)

    raise DynamicAttributeError("No such user: '%s'" % username)
