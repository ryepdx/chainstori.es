from chainstories import db

stories_snippets_table = db.Table("stories_snippets",
    db.Column("snippet_id", db.Integer, db.ForeignKey('snippet.id')),
    db.Column("story_id", db.Integer, db.ForeignKey('story.id'))
)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref = db.backref('stories', lazy = 'joined')
    )
    snippets = db.relationship("Snippet", secondary = stories_snippets_table,
        backref = db.backref('stories', lazy = 'dynamic')
    )

    def __init__(self, user, snippet):
        self.user = user
        self.text = snippet.text
        self.snippets = [ snippet ]

