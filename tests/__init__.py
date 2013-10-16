import os
import json
import unittest
import chainstories
import accesstoken
import user.models
import accesstoken.models
import snippet
import snippet.models
import story
import story.models

class AccessTokenGenerationTestCase(unittest.TestCase):
    def test_token_generation(self):
        token = accesstoken.generate_token(
            chars = accesstoken.TOKEN_CHARS,
            size = accesstoken.TOKEN_SIZE
        )
        assert len(token) == accesstoken.TOKEN_SIZE
        assert len([x for x in token if x not in accesstoken.TOKEN_CHARS]) == 0


class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        chainstories.app.config['DATABASE'] = '/tmp/chainstory_test.db'
        chainstories.app.config['SQLALCHEMY_DATABASE_URI'] = (
            'sqlite:///%s' % chainstories.app.config['DATABASE']
        )
        self.app = chainstories.app.test_client()
        chainstories.db.create_all()

    def tearDown(self):
        chainstories.db.session.remove()
        chainstories.db.drop_all()

    def login(self, username, password):
        return self.app.post('/accesstoken', data = {
            "username": username,
            "password": password
        }, follow_redirects = True)

    def logout(self):
        return self.app.delete('/accesstoken', follow_redirects = True)

    def signup(self, username, password, email=None):
        userdata = {
            "username": username,
            "password": password
        }
        if email:
            userdata["email"] = email

        return self.app.post('/user', data = userdata, follow_redirects = True)


class UserIntegrationTestCase(IntegrationTestCase):
    def setUp(self):
        super(UserIntegrationTestCase, self).setUp()
        self.username = "username"
        self.password = "password"
        self.user = user.models.User(self.username, self.password)
        chainstories.db.session.add(self.user)
        chainstories.db.session.commit()

    def given_an_authenticated_user(self):
        self.login(self.username, self.password)
        return self

class UserModelTestCase(IntegrationTestCase):
    def test_create_user(self):
        username = "username"
        password = "password"

        user_obj = user.models.User(username, password)
        chainstories.db.session.add(user_obj)
        chainstories.db.session.commit()

        found_obj = user.models.User.query.filter_by(
            username = username).first()

        assert found_obj != None
        assert found_obj == user_obj
        assert found_obj.check_password(password)


class AccessTokenModelTestCase(UserIntegrationTestCase):
    def test_create_access_token(self):
        token = accesstoken.models.AccessToken(
            self.user, accesstoken.generate_token())
        chainstories.db.session.add(token)
        chainstories.db.session.commit()

        assert self.user.get_auth_token() == token.token
        assert token.user == self.user
    

class SnippetTestCase(UserIntegrationTestCase):
    def test_create_snippets(self):
        self.login(self.username, self.password)
        rv = self.app.post("/snippet.json", data = {
            "text": "Some text."
        }, follow_redirects = True)
        
        json_data = json.loads(rv.data)["data"]
        assert "Some text." == json_data["text"]

        rv = self.app.post("/snippet", data = {
            "text": "More text.",
            "parent_id": json_data["id"]
        }, follow_redirects = True)

        assert "More text." in rv.data
        assert snippet.CREATED_MESSAGE in rv.data


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
        assert self.parent_snippet["text"] == self.story["text"]
        return self

    def when_I_add_the_child_snippet_to_the_story(self):
        rv = self.app.post("/story/%s/snippets.json" % self.story["id"],
            data = { "snippet_id": self.child_snippet["id"] })
        self.snippets = json.loads(rv.data)["data"]
        return self

    def then_story_snippets_should_contain_child_snippet(self):
        assert len([x for x in self.snippets
            if x["id"] == self.child_snippet["id"]]) == 1
        assert len([x for x in self.snippets
            if x["text"] == self.child_snippet["text"]]) > 0

    def then_story_should_consist_of_parent_and_child_snippet(self):
        expected_text = "%s %s" % (
            self.parent_snippet["text"],
            self.child_snippet["text"]
        )
        story = json.loads(
            self.app.get("/story/%s.json" % self.story["id"]).data
        )["data"]
        assert story["text"] == expected_text

        rv = self.app.get("/story/%s" % self.story["id"])
        assert expected_text in rv.data

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


class HomeTestCase(IntegrationTestCase):
    def test_empty_db(self):
        rv = self.app.get('/home')
        assert 'No stories yet!' in rv.data


class UserUITestCase(IntegrationTestCase):
    def test_user_signup_and_login(self):
        rv = self.app.post("/user", follow_redirects = True)
        assert "Missing parameters." in rv.data

        rv = self.login('badusername','badpassword')
        assert 'Invalid username or password!' in rv.data

        rv = self.signup('goodusername', 'goodpassword')
        assert user.WELCOME_GREETING in rv.data

        rv = self.logout()
        assert accesstoken.LOGGED_OUT in rv.data

        rv = self.login("goodusername", "goodpassword")
        assert accesstoken.LOGGED_IN in rv.data

    def test_user_signup_and_profile(self):
        rv = self.signup("user1", "password1")
        assert user.WELCOME_GREETING in rv.data

        rv = self.app.get("/user/user1")
        assert "This user has not written anything yet!" in rv.data
