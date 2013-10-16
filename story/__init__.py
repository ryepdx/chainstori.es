import flask
from chainstories import db
from cyborg import DynamicAttributeError
from story.models import Story
from snippet.models import Snippet

class StoryHandler(object):
    def __init__(self, story_obj):
        self.story = story_obj

    @property
    def get(self):
        return self

    @property
    def snippets(self):
        return SnippetsHandler(self.story, self.story.snippets)

    def machine(self, request):
        return { "data":
            { "id": self.story.id, "text": self.story.text }
        }

    def human(self, request):
        return flask.render_template("story.html", **self.machine(request)["data"])


class SnippetsHandler(object):
    def __init__(self, story, snippets):
        self.story = story
        self.snippets = snippets

    @property
    def post(self):
        return SnippetsPostHandler(self.story, self.snippets)


class SnippetsPostHandler(object):
    def __init__(self, story, snippets):
        self.snippets = snippets
        self.story = story

    def machine(self, request):
        if "snippet_id" not in request.form:
            return { "error": "Missing parameters." }

        snippet = Snippet.query.get(request.form["snippet_id"])
        
        if not snippet:
            return { "error": "Invalid snippet ID." }

        self.story.snippets.append(snippet)
        self.story.text += (" %s" % snippet.text)
        db.session.commit()
    
        return { "data": [
            { "id": x.id, "text": x.text } for x in self.snippets
        ]}

def __getattr__(story_id):
    story_obj = Story.query.get(story_id)
    
    if not story_obj:
        raise DynamicAttributeError("Could not find story %s" % story_id)

    return StoryHandler(story_obj)
