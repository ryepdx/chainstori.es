import bcrypt
from chainstories import db
from flask.ext.login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable = False)
    passhash = db.Column(db.BINARY(length = 60), nullable = False)
    email = db.Column(db.String(120))

    def __init__(self, username, password, email = None):
        self.username = username
        self.passhash = bcrypt.hashpw(password, bcrypt.gensalt())
        self.email = email

    def check_password(self, password):
        return bcrypt.hashpw(password, self.passhash) == self.passhash

    # Required by Flask-Login
    def get_auth_token(self):
        if self.access_tokens:
            return self.access_tokens[0].token
        return None
