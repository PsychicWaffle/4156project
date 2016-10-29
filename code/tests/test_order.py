import unittest
import app
from app import order

class LoginTest(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_order_size(self):
        temp_order = order.Order(10, 1000)
        order_size = temp_order.get_next_order_size()
        self.assertGreater(order_size, 0)

if __name__ == '__main__':
        unittest.main()

