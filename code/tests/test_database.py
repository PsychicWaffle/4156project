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

        def test_update_user_password(self):
                test_username = "Jacob"
                test_passhash = "3838"
                test_passhash_new = "4949"
                dm.insertNewUser(test_username, test_passhash)
                dm.updateUserPassword(test_username, test_passhash_new)
                returned_user = dm.getUser(test_username)
                self.assertTrue(returned_user.password == "4949")
                dm.removeUser(test_username)
	
        def test_insert_item_with_id(self):
                test_username = "Sam"
                test_passhash = "dfjlkd"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                returned_transactions = dm.getAllTransactionList(test_username)
                self.assertTrue(len(returned_transactions) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_update_transacton_status(self):
                test_username = "Sam"
                test_passhash = "dfjlkd"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                dm.updateTransactionQueuedStatus(ret, False)
                returned_transactions = dm.getAllTransactionList(test_username)
                self.assertTrue(len(returned_transactions) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_max_trans_id(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                max_id = dm.getMaxTransactionId(test_username)
                self.assertTrue(max_id == 1)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_grouped_trans_list(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                transaction = Transactions(username=test_username, finished=True, qty_requested=200, qty_executed=0, timestamp=time.time(), queued=False, order_type=2, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                dm.insertNewExecutedTrade(ret, 1, 10, 40)
                trans_list = dm.getGroupedTransactionList(test_username, completed=True)
                trans_list = dm.getGroupedTransactionList(test_username, completed=True, date_format="%b %d %Y %H:%M:%S")
                self.assertTrue(len(trans_list) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_grouped_trans_list_execpos(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=True, qty_requested=100, qty_executed=10, timestamp=time.time(), queued=False, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                trans_list = dm.getGroupedTransactionList(test_username, completed=True)
                self.assertTrue(len(trans_list) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_grouped_trans_notinrange(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                trans_list = dm.getGroupedTransactionList(test_username, start_date=0, end_date=-1)
                self.assertTrue(len(trans_list) == 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_grouped_trans_minqtyexec(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                trans_list = dm.getGroupedTransactionList(test_username, min_qty_executed=10)
                self.assertTrue(len(trans_list) == 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_grouped_trans_maxqtyexec(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=10, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                trans_list = dm.getGroupedTransactionList(test_username, max_qty_executed=0)
                self.assertTrue(len(trans_list) == 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_active_trans_list(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                transaction = Transactions(username=test_username, finished=False, qty_requested=200, qty_executed=0, timestamp=time.time(), queued=False, order_type=2, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                dm.insertNewExecutedTrade(ret, 1, 10, 40)
                trans_list = dm.getActiveTransactionList(test_username)
                self.assertTrue(len(trans_list) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_get_active_trans(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                transaction = Transactions(username=test_username, finished=False, qty_requested=200, qty_executed=0, timestamp=time.time(), queued=False, order_type=2, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                dm.insertNewExecutedTrade(ret, 1, 10, 40)
                trans_list = dm.getActiveTransactions(test_username)
                self.assertTrue(len(trans_list) > 0)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_remove_exec_trade(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=200, qty_executed=0, timestamp=time.time(), queued=False, order_type=2, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                tid = dm.insertNewExecutedTrade(ret, 1, 10, 40)
                dm.removeExecutedTradesById(ret)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

        def test_remove_trans_byid(self):
                test_username = "Jake"
                test_passhash = "3838"
                dm.insertNewUser(test_username, test_passhash)
                transaction = Transactions(username=test_username, finished=False, qty_requested=100, qty_executed=0, timestamp=time.time(), queued=True, order_type=0, min_price = -1)
                ret = dm.insertDatabaseItemWithId(transaction)
                dm.removeTransactionsById(ret)
                dm.removeTransactionsByUsername(test_username)
                dm.removeUser(test_username)

if __name__ == '__main__':
	unittest.main()
