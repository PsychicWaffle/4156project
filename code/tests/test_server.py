import sys
sys.path.append('app')
import os
import server
import unittest
import tempfile

class ServerTest(unittest.TestCase):
    
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        
    def test_root(self):
        ret = self.app.get('/')
        self.assertTrue(ret != None)

    def test_home(self):
        ret = self.app.get('/home')
        self.assertTrue(ret != None)

    def test_track_order(self):
        ret = self.app.get('/track_order')
        self.assertTrue(ret != None)

    def test_change(self):
        ret = self.app.get('/change')
        self.assertTrue(ret != None)

    def test_create(self):
        ret = self.app.get('/create')
        self.assertTrue(ret != None)

    def test_login(self):
        ret = self.app.get('/login')
        self.assertTrue(ret != None)

    def tearDown(self):
        pass

if __name__ == '__main__':
       DATABASE_URI = "sqlite://"
       database_methods.engine = create_engine(DATABASE_URI)
       database_methods.Session = sessionmaker(bind=database_methods.engine)
       unittest.main()

