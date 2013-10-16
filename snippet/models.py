from chainstories import db

class Snippet(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref = db.backref('snippets', lazy = 'joined')
    )
    parent_id = db.Column(db.Integer, db.ForeignKey('snippet.id'), nullable = True)
    children = db.relationship('Snippet',
        backref = db.backref('parent', lazy = 'select'),
        remote_side = [id]
    )

    def __init__(self, user, text, parent = None):
        if parent:
            self.parent = parent
        
        self.user = user
        self.text = text

