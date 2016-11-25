import sys
import time
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('app')
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

	def test_create_new_user(self):
                test_username = "Andy"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                returned_user = dm.getUser(test_username)
                self.assertTrue(returned_user != None)
                dm.removeUser(test_username)
	
        def test_insert_item_with_id(self):
                test_username = "Sam"
                test_passhash = "dfjlkd"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True)
                ret = dm.insertDatabaseItemWithId(transaction)
                returned_transactions = dm.getAllTransactionList(test_username)
                self.assertTrue(len(returned_transactions) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

if __name__ == '__main__':
	unittest.main()
