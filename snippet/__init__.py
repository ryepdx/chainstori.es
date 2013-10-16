import flask
from snippet.models import Snippet
from cyborg import DynamicAttributeError

CREATED_MESSAGE = "Snippet created!"

class SnippetHandler(object):
    def __init__(self, snippet):
        self.snippet = snippet

    @property
    def get(self):
        return self

    def machine(self, request):
        return { "data":
            {
                "id": self.snippet.id,
                "text": self.snippet.text,
                "parent": {} if not self.snippet.parent else {
                    "id": self.snippet.parent.id,
                    "href": "/snippet/%s" % self.snippet.parent.id
                },
                "children": {} if not self.snippet.children else {
                    "data": [ {
                        "id": x.id,
                        "text": x.text,
                        "href": "/snippet/%s" % x.id
                    } for x in self.snippet.children ]
                }
            }
        }

    def human(self, request):
        return flask.render_template(
            "snippet.html", **self.machine(request)["data"]
        )


def __getattr__(snippet_id):
    snippet_obj = Snippet.query.get(snippet_id)

    if not snippet_obj:
        raise DynamicAttributeError("Could not find snippet %s" % snippet_id)

    return SnippetHandler(snippet_obj)

