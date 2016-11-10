import sys
sys.path.append('app')
import os
import server
import unittest
import tempfile
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import database_methods
import database_objects

class ServerTest(unittest.TestCase):

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        DATABASE_URI = "sqlite://"
        database_methods.engine = create_engine(DATABASE_URI)
        database_methods.Session = sessionmaker(bind=database_methods.engine)
        database_methods.createSchema()
        pass

    def test_root(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/')
        self.assertTrue(ret != None)

    def test_home(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/home')
        self.assertTrue(ret != None)

    def test_track_order(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/track_order')
        self.assertTrue(ret != None)

    def test_history(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/history')
        self.assertTrue(ret != None)

    def test_change(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/change')
        self.assertTrue(ret != None)

    def test_create(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.get('/create')
        self.assertTrue(ret != None)

    def test_nologin(self):
        ret = self.app.get('/home')
        self.assertTrue(ret.headers['Location'] == 'http://localhost/login')

    def test_negative_order_size_input(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.post('/home', data=dict(
               quantity="-1"
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def test_zero_order_size_input(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.post('/home', data=dict(
               quantity="0"
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def test_char_order_size_input(self):
        self.create_user('test', 'test')
        self.login('test', 'test')
        ret = self.app.post('/home', data=dict(
               quantity="hey"
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def create_user(self, username, password):
        return self.app.post('/create', data=dict(
            username=username,
            password=password,
            password_conf=password
        ), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        # Create a test user, make sure we are redirected
        ret = self.create_user('test', 'test')
        assert('Please login' in ret.data or 'User name already exists' in ret.data)

        # Test that we can login
        ret = self.login('test', 'test')
        assert('Hello, test!' in ret.data)

        # Test that we can logout
        ret = self.logout()
        assert('Please login' in ret.data)

        # Make sure that we aren't still logged in incorrectly
        ret = self.app.get('/home', follow_redirects=True)
        assert('Please login' in ret.data)

    def test_bad_login(self):
        ret = self.login('bad_user', 'bad_password')
        assert("Incorrect username or password" in ret.data)

    def test_bad_password(self):
        ret = self.create_user('test', 'test')
        assert('Please login' in ret.data or 'User name already exists' in ret.data)

        ret = self.login('test', 'bad_password')
        assert("Incorrect username or password" in ret.data)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

