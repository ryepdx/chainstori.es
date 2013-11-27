import json

from . import LOGGER, UserIntegrationTestCase, ok_, in_, eq_


class StoryTestCase(UserIntegrationTestCase):
    def given_a_parent_snippet(self):
        rv = self.app.post("/snippet.json", data = {
            "text": "Once upon a time...",
        }, follow_redirects = True)
        self.parent_snippet = json.loads(rv.data)["data"]
        return self

    def given_a_child_snippet(self):
        rv = self.app.post("/snippet.json", data = {
            "text": "The End.",
            "parent_id": self.parent_snippet["id"]
        }, follow_redirects = True)
        self.child_snippet = json.loads(rv.data)["data"]
        return self

    def when_I_create_a_story_with_the_parent_snippet(self):                
        rv = self.app.post("/story.json", data = {
            "snippet_id": self.parent_snippet["id"]
        })
        self.story = json.loads(rv.data)["data"]
        return self

    def then_story_text_should_equal_parent_snippet_text(self):
        eq_(self.parent_snippet["text"], self.story["text"])
        return self

    def when_I_add_the_child_snippet_to_the_story(self):
        rv = self.app.post("/story/%s/snippets.json" % self.story["id"],
            data = { "snippet_id": self.child_snippet["id"] })
        try:
            self.snippets = json.loads(rv.data)["data"]
        except ValueError:
            LOGGER.error("Could not load JSON from '%s'" % rv.data)
            raise
        return self

    def then_story_snippets_should_contain_child_snippet(self):
        ok_(len([x for x in self.snippets
            if x["id"] == self.child_snippet["id"]]) == 1,
            msg = "Could not find ID '%s' in '%s'" % (
                self.child_snippet["id"], 
                "','".join([x["id"] for x in self.snippets])
            )
        )

        ok_(len([x for x in self.snippets
            if x["text"] == self.child_snippet["text"]]) > 0,
            msg = "Could not find '%s' in '%s'" % (
                self.child_snippet["text"], 
                "','".join([x["text"] for x in self.snippets])
            )
        )

    def then_story_should_consist_of_parent_and_child_snippet(self):
        expected_text = "%s %s" % (
            self.parent_snippet["text"],
            self.child_snippet["text"]
        )
        story = json.loads(
            self.app.get("/story/%s.json" % self.story["id"]).data
        )["data"]
        eq_(story["text"], expected_text)

        rv = self.app.get("/story/%s" % self.story["id"])
        in_(expected_text, rv.data)

        return self
        
    def test_create_simple_story(self):
        (self.given_an_authenticated_user()
             .given_a_parent_snippet()
             .when_I_create_a_story_with_the_parent_snippet()
             .then_story_text_should_equal_parent_snippet_text()
        )

    def test_create_composite_story(self):
        (self.given_an_authenticated_user()
             .given_a_parent_snippet()
             .given_a_child_snippet()
             .when_I_create_a_story_with_the_parent_snippet()
             .when_I_add_the_child_snippet_to_the_story()
             .then_story_should_consist_of_parent_and_child_snippet()
        )


