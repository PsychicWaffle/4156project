import unittest
from app import validity_checker

class ValidityCheckerClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_valid_history_date_range_1(self):
        start_date = -1
        end_date = 100
        valid_date_range = validity_checker.valid_history_date_range(start_date, end_date)
        self.assertTrue(valid_date_range == False)

    def test_valid_history_date_range_2(self):
        start_date = 100
        end_date = 200
        valid_date_range = validity_checker.valid_history_date_range(start_date, end_date)
        self.assertTrue(valid_date_range == True)

    def test_valid_history_date_range_3(self):
        start_date = 100
        end_date = 50
        valid_date_range = validity_checker.valid_history_date_range(start_date, end_date)
        self.assertTrue(valid_date_range == False)

    def test_order_size_1(self):
        big_order_size = validity_checker.MAX_ORDER_SIZE
        big_order_size = big_order_size + 1
        valid_order = validity_checker.valid_order_parameters(big_order_size)
        self.assertTrue(valid_order == False)

    def test_order_size_2(self):
        order_size = validity_checker.MAX_ORDER_SIZE - 1
        valid_order = validity_checker.valid_order_parameters(order_size)
        self.assertTrue(valid_order == True)

    def test_order_username_1(self):
        username = "A"
        valid_order = validity_checker.valid_username(username)
        self.assertTrue(valid_order == False)

    def test_order_username_2(self):
        username = "Andrew"
        valid_order = validity_checker.valid_username(username)
        self.assertTrue(valid_order == True)

    def test_order_password_1(self):
        password = "a"
        valid_order = validity_checker.valid_username(password)
        self.assertTrue(valid_order == False)

    def test_order_username_2(self):
        password = "dklfjdkfjl"
        valid_order = validity_checker.valid_username(password)
        self.assertTrue(valid_order == True)
