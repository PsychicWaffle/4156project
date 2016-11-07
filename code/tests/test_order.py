import unittest
import app
from app import order

class LoginTest(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_next_order(self):
        temp_order = order.Order(10, 1000)
        next_order = temp_order.get_next_order()
        self.assertTrue(next_order != None)

    def test_order_size(self):
        temp_order = order.Order(10, 1000)
        order_size = temp_order.get_next_order_size()
        self.assertGreater(order_size, 0)

    def test_order_time(self):
        temp_order = order.Order(10, 1000)
        order_time = temp_order.get_next_order_time()
        self.assertTrue(order_time != None)

    def test_process_exectuted_order(self):
        temp_order = order.Order(10, 1000)
        ret = temp_order.process_executed_order(10, 10.0, 1000)
        self.assertTrue(ret == 1)

    def test_get_inventory_left(self):
        temp_order = order.Order(10, 1000)
        ret = temp_order.get_inventory_left()
        self.assertTrue(ret == 10)

    def test_get_executed_trades(self):
        temp_order = order.Order(10, 1000)
        ret = temp_order.get_executed_trades()
        self.assertTrue(len(ret) == 0)

if __name__ == '__main__':
       DATABASE_URI = "postgresql://localhost/master_4156_database_test"
       database_methods.engine = create_engine(DATABASE_URI)
       database_methods.Session = sessionmaker(bind=database_methods.engine)
       unittest.main()

