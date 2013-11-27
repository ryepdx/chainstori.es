import accesstoken
import user.models
import chainstories

from . import IntegrationTestCase, ok_, eq_, in_

class UserModelTestCase(IntegrationTestCase):
    def test_create_user(self):
        username = "username"
        password = "password"

        user_obj = user.models.User(username, password)
        chainstories.db.session.add(user_obj)
        chainstories.db.session.commit()

        found_obj = user.models.User.query.filter_by(
            username = username).first()

        ok_(found_obj != None)
        eq_(found_obj, user_obj)
        ok_(found_obj.check_password(password))
   

class UserUITestCase(IntegrationTestCase):
    def test_user_signup_and_login(self):
        rv = self.app.post("/user", follow_redirects = True)
        in_("Missing parameters.", rv.data)

        rv = self.login('badusername','badpassword')
        in_('Invalid username or password!', rv.data)

        rv = self.signup('goodusername', 'goodpassword')
        in_(user.WELCOME_GREETING, rv.data)

        rv = self.logout()
        in_(accesstoken.LOGGED_OUT, rv.data)

        rv = self.login("goodusername", "goodpassword")
        in_(accesstoken.LOGGED_IN, rv.data)

    def test_user_signup_and_profile(self):
        rv = self.signup("user1", "password1")
        in_(user.WELCOME_GREETING, rv.data)

        rv = self.app.get("/user/user1")
        in_("This user has not written anything yet!", rv.data)
