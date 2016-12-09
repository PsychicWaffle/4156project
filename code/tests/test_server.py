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
    TEST_USERNAME='test'
    TEST_PASSWORD='test'

    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        DATABASE_URI = "sqlite://"
        database_methods.engine = create_engine(DATABASE_URI)
        database_methods.Session = sessionmaker(bind=database_methods.engine)
        database_methods.createSchema()
        pass

    def test_root(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/')
        self.assertTrue(ret != None)

    def test_home(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/home')
        self.assertTrue(ret != None)

    def test_track_order(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/track_order')
        self.assertTrue(ret != None)

    def test_get_history(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/history')
        self.assertTrue(ret != None)

    def test_history_no_date(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="",
               end_date="10"
               ), follow_redirects=True)
        self.assertTrue('No quantity given' in ret.data)

    def test_history_bad_start_range(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="-1",
               end_date="10"
               ), follow_redirects=True)
        self.assertTrue('Invalid date range' in ret.data)

    def test_history_bad_end_range(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="1",
               end_date="-1"
               ), follow_redirects=True)
        self.assertTrue('Invalid date range' in ret.data)

    def test_history_bad_date_range(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="5",
               end_date="4"
               ), follow_redirects=True)
        self.assertTrue('Invalid date range' in ret.data)

    def test_history_char_start_date(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="a",
               end_date="4"
               ), follow_redirects=True)
        self.assertTrue('Invalid date range' in ret.data)

    def test_history_char_end_date(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/history', data=dict(
               start_date="4",
               end_date="b"
               ), follow_redirects=True)
        self.assertTrue('Invalid date range' in ret.data)

    def test_change(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/change')
        self.assertTrue(ret != None)

    def test_change_nousername(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/change', data=dict(
            username=""
            ), follow_redirects=True)
        self.assertTrue('No username given' in ret.data)

    def test_change_nopassword(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/change', data=dict(
            username="joe",
            password=""
            ), follow_redirects=True)
        self.assertTrue('No password given' in ret.data)

    def test_change_newpass_nomatch(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/change', data=dict(
            username="jake",
            password="maybe",
            new_password="no",
            password_conf="yes"
            ), follow_redirects=True)
        self.assertTrue('Passwords must match' in ret.data)

    def test_change_password_good(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/change', data=dict(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            new_password="newpass",
            password_conf="newpass"
            ), follow_redirects=True)
        self.assertTrue(ret != None)

    def test_change_password_wrongold(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/change', data=dict(
            username=self.TEST_USERNAME,
            password="wrong",
            new_password="newpass",
            password_conf="newpass"
            ), follow_redirects=True)
        self.assertTrue('Incorrect username or password' in ret.data)

    def test_create(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.get('/create')
        self.assertTrue(ret != None)

    def test_create_nouser(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/create', data=dict(
            username=""
            ), follow_redirects=True)
        self.assertTrue('No username given' in ret.data)

    def test_create_nopass(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/create', data=dict(
            username="joe",
            password=""
            ), follow_redirects=True)
        self.assertTrue('No password given' in ret.data)

    def test_create_nomatch(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/create', data=dict(
            username="jake",
            password="maybe",
            password_conf="maybenot"
            ), follow_redirects=True)
        self.assertTrue('Passwords must match' in ret.data)

    def test_create_userexists(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/create', data=dict(
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            password_conf=self.TEST_PASSWORD
            ), follow_redirects=True)
        self.assertTrue('User name already exists' in ret.data)

    def test_nologin(self):
        ret = self.app.get('/home')
        self.assertTrue(ret.headers['Location'] == 'http://localhost/login')

    def test_history_start_date(self):
        self.assertTrue(1 == 1)

    def test_order_type2_nomin_input(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/home', data=dict(
               quantity=100,
               order_type=2,
               min_price=""
               ), follow_redirects=True)
        self.assertTrue('Invalid limit order given: No min price given' in ret.data)

    def test_order_type2_negmin_input(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/home', data=dict(
               quantity=100,
               order_type=2,
               min_price=-1
               ), follow_redirects=True)
        self.assertTrue('Invalid limit order given: min price cannot be less than 0' in ret.data)

    def test_negative_order_size_input(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/home', data=dict(
               quantity="-1",
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def test_zero_order_size_input(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/home', data=dict(
               quantity="0"
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def test_char_order_size_input(self):
        self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
        ret = self.app.post('/home', data=dict(
               quantity="hey"
               ), follow_redirects=True)
        self.assertTrue('Invalid parameters' in ret.data)

    def test_get_market_price(self):
        ret = self.app.get('/market_price_request')
        self.assertTrue(ret != None)

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
        ret = self.create_user(self.TEST_USERNAME, self.TEST_PASSWORD)
        assert('Please login' in ret.data or 'User name already exists' in ret.data)

        # Test that we can login
        ret = self.login(self.TEST_USERNAME, self.TEST_PASSWORD)
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
        ret = self.create_user('bad_test', self.TEST_PASSWORD)
        assert('Please login' in ret.data or 'User name already exists' in ret.data)

        ret = self.login('bad_test', 'bad_password')
        assert("Incorrect username or password" in ret.data)

    def test_invalid_new_username(self):
        ret = self.create_user('a', 'password')
        self.assertTrue('Invalid username' in ret.data)

    def test_invalid_new_password(self):
        ret = self.create_user('andrew', 'p')
        self.assertTrue('Invalid password' in ret.data)

    def tearDown(self):
        pass

    def test_command_args_onearg(self):
        server.process_command_line_args(["arg1"])
        pass

    def test_command_args_prices(self):
        server.process_command_line_args(["server.py", "print_prices"])

if __name__ == '__main__':
    unittest.main()

