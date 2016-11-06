import sys
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('../app')
import unittest
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from database_objects import *
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

	def test_insert_item_with_id(self):
		transaction = Transactions(username='test', finished=False, qty_requested=100, qty_executed=0)
		ret = dm.insertDatabaseItemWithId(transaction)
		self.assertEqual(ret, 1)

		transaction = Transactions(username='test', finished=False, qty_requested=200, qty_executed=0)
		ret = dm.insertDatabaseItemWithId(transaction)
		self.assertEqual(ret, 2)

if __name__ == '__main__':
	unittest.main()
