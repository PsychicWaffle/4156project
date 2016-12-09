import unittest
import app
from app import order

class OrderTest(unittest.TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_next_order(self):
        temp_order = order.Order(10, 1000)
        next_order = temp_order.get_next_order()
        self.assertTrue(next_order != None)

    def test_get_next_order_type2(self):
        temp_order = order.Order(10, 1000, order_type=2, min_price=1000)
        next_order = temp_order.get_next_order()
        self.assertTrue(next_order != None)

    def test_get_next_order_type2_recalc(self, recalc=True):
        temp_order = order.Order(10, 1000, order_type=2, min_price=0)
        next_order = temp_order.get_next_order(True)
        self.assertTrue(next_order != None)

    def test_get_next_order_type1(self, recalc=True):
        temp_order = order.Order(10, 1000, order_type=1)
        next_order = temp_order.get_next_order(True)
        self.assertTrue(next_order != None)

    def test_order_size(self):
        temp_order = order.Order(10, 1000)
        (order_size, _) = temp_order.get_next_order()
        self.assertGreater(order_size, 0)

    def test_order_time(self):
        temp_order = order.Order(10, 1000)
        (_, order_time) = temp_order.get_next_order()
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

    def test_negative_order_size(self):
        try:
            temp_order = order.Order(-1, 1000)
            caught_ex = False
        except ValueError:
            caught_ex = True
        self.assertTrue(caught_ex == True)

    def test_big_order_size(self):
        try:
            temp_order = order.Order(-100, 1000)
            caught_ex = False
        except ValueError:
            caught_ex = True
        self.assertTrue(caught_ex == True)

    def test_negative_start_time(self):
        try:
            temp_order = order.Order(1, -1)
            caught_ex = False
        except ValueError:
            caught_ex = True
        self.assertTrue(caught_ex == True)

    def test_big_negative_start_time(self):
        try:
            temp_order = order.Order(1, -100)
            caught_ex = False
        except ValueError:
            caught_ex = True
        self.assertTrue(caught_ex == True)

if __name__ == '__main__':
       DATABASE_URI = "sqlite://"
       database_methods.engine = create_engine(DATABASE_URI)
       database_methods.Session = sessionmaker(bind=database_methods.engine)
       unittest.main()

