import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('../app')
import unittest
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import database_objects as do
import database_methods as dm

class DatabaseTest(unittest.TestCase):
	def setUp(self):
		DATABASE_URI = "sqlite://"
		dm.engine = create_engine(DATABASE_URI)
		dm.Session = sessionmaker(bind=dm.engine)
		dm.createSchema()
		pass

	def tearDown(self):
		pass

	def test_order_size(self):
		self.assertEqual(0, 0)

if __name__ == '__main__':
	unittest.main()
