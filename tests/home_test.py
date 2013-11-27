from . import IntegrationTestCase, in_, eq_, ok_

class HomeTestCase(IntegrationTestCase):
    def test_empty_db(self):
        rv = self.app.get('/home')
        in_('Login', rv.data)


