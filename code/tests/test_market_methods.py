import sys
sys.path.append('app')
import os
import unittest
import tempfile
import server
import market_methods
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class MarketMethodsTest(unittest.TestCase):
    def setUp(self):
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        DATABASE_URI = "sqlite://"

    def test_get_market_time(self):
        curr_time = market_methods.get_market_time()
        self.assertTrue(curr_time != None)
        self.assertTrue(type(curr_time) == float)
        self.assertTrue(curr_time >= 0)
        
    def test_get_market_quote(self):
        quote = market_methods.get_market_quote()
        self.assertTrue(quote != None)

    def test_get_market_time_formatted(self):
        curr_time = market_methods.get_market_time_formatted("%Y-%m-%d %H:%M:%S.%f")
        self.assertTrue(isinstance(curr_time, (str, unicode)) == True)
        self.assertTrue(curr_time != None)

    def test_get_price(self):
        curr_price = market_methods.get_market_price()
        self.assertTrue(curr_price != None)
        self.assertTrue(curr_price >= 0)

    def test_get_beg_time(self):
        seconds = market_methods.get_beg_of_day_time()
        self.assertTrue(seconds > 0)

    def test_timestamp_today(self):
        ret = market_methods.timestamp_from_today(9999999999999999999999)
        self.assertTrue(ret)
        ret = market_methods.timestamp_from_today(0)
        self.assertFalse(ret)

    def tearDown(self):
        pass
