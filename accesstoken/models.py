from chainstories import db

class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref = db.backref('access_tokens', lazy = 'joined'),
        uselist = False
    )

    def __init__(self, user, token):
        self.user = user
        self.token = token
