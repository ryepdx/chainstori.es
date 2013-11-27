import unittest
import accesstoken
import chainstories

from . import UserIntegrationTestCase, eq_, ok_, in_

class AccessTokenGenerationTestCase(unittest.TestCase):
    def test_token_generation(self):
        token = accesstoken.generate_token(
            chars = accesstoken.TOKEN_CHARS,
            size = accesstoken.TOKEN_SIZE
        )
        eq_(len(token), accesstoken.TOKEN_SIZE)
        eq_(len([x for x in token if x not in accesstoken.TOKEN_CHARS]), 0)


class AccessTokenModelTestCase(UserIntegrationTestCase):
    def test_create_access_token(self):
        token = accesstoken.models.AccessToken(
            self.user, accesstoken.generate_token())
        chainstories.db.session.add(token)
        chainstories.db.session.commit()

        eq_(self.user.get_auth_token(), token.token)
        eq_(token.user, self.user)
 
