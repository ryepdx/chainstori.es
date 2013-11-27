import json
import snippet

from . import UserIntegrationTestCase, ok_, eq_, in_

class SnippetTestCase(UserIntegrationTestCase):
    def test_create_snippets(self):
        self.login(self.username, self.password)
        rv = self.app.post("/snippet.json", data = {
            "text": "Some text."
        }, follow_redirects = True)
        
        json_data = json.loads(rv.data)["data"]
        eq_("Some text.", json_data["text"])

        rv = self.app.post("/snippet", data = {
            "text": "More text.",
            "parent_id": json_data["id"]
        }, follow_redirects = True)

        in_("More text.", rv.data)
        assert snippet.CREATED_MESSAGE in rv.data
