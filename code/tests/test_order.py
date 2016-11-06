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
       DATABASE_URI = "postgresql://localhost/master_4156_database_test"
       database_methods.engine = create_engine(DATABASE_URI)
       database_methods.Session = sessionmaker(bind=database_methods.engine)
       unittest.main()

