import os
import logging
import unittest
import chainstories
import user.models

import nose.tools
from nose.tools import ok_

LOGGER = logging.getLogger(__name__)

def eq_(thing1, thing2, msg = None):
    """Nose.tools.eq_ with a helpful default message"""
    return nose.tools.eq_(thing1, thing2,
        msg = (msg if msg != None else "'%s' != '%s'" % (thing1, thing2))
    )

def in_(needle, haystack, msg = None):
    """Helper function for the ok_(x in y) pattern, with a default message"""
    return nose.tools.ok_(needle in haystack,
        msg = (msg if msg != None else "'%s' not in '%s'" % (needle, haystack))
    )


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
