import os
import tempfile
import unittest
import chainstories
import accesstoken
import user.models
import accesstoken.models
import snippet
import snippet.models

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
        rv = self.app.post("/snippet", data = {
            "text": "Some text."
        }, follow_redirects = True)
        assert snippet.CREATED_MESSAGE in rv.data


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
