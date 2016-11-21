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
from transaction import *

class TransactionTest(unittest.TestCase):

    def setUp(self):
        DATABASE_URI = "sqlite://"
        database_methods.engine = create_engine(DATABASE_URI)
        database_methods.Session = sessionmaker(bind=database_methods.engine)
        database_methods.createSchema()

    def test_1(self):
        self.assertTrue(1 == 1)
        
    def test_execute_transaction(self):
        test_username = "Andy"
        test_passhash = "3838"
        test_trade_quantity = 1
        database_methods.insertNewUser(test_username, test_passhash)
        returned_user = database_methods.getUser(test_username)
        self.assertTrue(returned_user != None)
        ret_id = database_methods.insertNewTransaction(test_trade_quantity, test_username)
        test_t_x = TransactionExecuter(test_trade_quantity, test_username, ret_id)
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        test_t_x_finished = False
        test_t_x.execute_transaction()
        while (test_t_x_finished == False):
            curr_tran = database_methods.getTransactionById(ret_id)
            if (curr_tran.finished == True):
                test_t_x_finished = True

        sys.stdout = old_stdout

    def test_negative_order_size(self):
        test_username = "Andy"
        test_passhash = "3838"
        test_trade_quantity = -1
        database_methods.insertNewUser(test_username, test_passhash)
        returned_user = database_methods.getUser(test_username)
        self.assertTrue(returned_user != None)
        ret_id = database_methods.insertNewTransaction(test_trade_quantity, test_username)
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            test_t_x = TransactionExecuter(test_trade_quantity, test_username, ret_id)
            test_t_x.execute_transaction()
            caught_ex = False
        except ValueError:
            caught_ex = True

        sys.stdout = old_stdout
        self.assertTrue(caught_ex == True)

    def test_big_negative_order_size(self):
        test_username = "Andy"
        test_passhash = "3838"
        test_trade_quantity = -1000
        database_methods.insertNewUser(test_username, test_passhash)
        returned_user = database_methods.getUser(test_username)
        self.assertTrue(returned_user != None)
        ret_id = database_methods.insertNewTransaction(test_trade_quantity, test_username)
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            test_t_x = TransactionExecuter(test_trade_quantity, test_username, ret_id)
            test_t_x.execute_transaction()
            caught_ex = False
        except ValueError:
            caught_ex = True

        sys.stdout = old_stdout
        self.assertTrue(caught_ex == True)

if __name__ == '__main__':
    unittest.main()
