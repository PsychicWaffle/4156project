################################################################################
#
#  Permission is hereby granted, free of charge, to any person obtaining a 
#  copy of this software and associated documentation files (the "Software"), 
#  to deal in the Software without restriction, including without limitation 
#  the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#  and/or sell copies of the Software, and to permit persons to whom the 
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in 
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
#  DEALINGS IN THE SOFTWARE.

import urllib2
import time
import json
import random
import py_compile
from order import Order
from database_objects import *
from database_methods import *

class TransactionExecuter:
    # Server API URLs
    QUERY = "http://localhost:8080/query?id={}"
    ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"
    ORDER_DISCOUNT = 10
    N = 5

    def __init__(self, INVENTORY, username, trans_id):
        self.qty = INVENTORY
        self.username = username
        self.trans_id = trans_id

    def execute_transaction(self):
        '''
        Execute a transaction for a givent amount of inventory
        Method used from given sample in client.py
        '''
        # Start with all shares and no profit
        pnl = 0
        start_time = time.time()
        self.my_order = Order(self.qty, start_time)

        # Repeat the strategy until we run out of shares.
        while (self.my_order.get_inventory_left() > 0):
            price = self.__print_quotes()
            now = time.time()
            current_order_size, current_order_time = self.my_order.get_next_order()
            if now < current_order_time:
                continue
            self.attempt_to_execute_sub_order(current_order_size, current_order_time, price, pnl, now)

        self.__clean_up_transaction(pnl)

    def attempt_to_execute_sub_order(self, current_order_size, current_order_time, price, pnl, now):
        # Attempt to execute a sell order.
        order_args = (current_order_size, price - TransactionExecuter.ORDER_DISCOUNT)
        print "Executing 'sell' of {:,} @ {:,}".format(*order_args)
        url   = TransactionExecuter.ORDER.format(random.random(), *order_args)
        order = json.loads(urllib2.urlopen(url).read())

        # Update the PnL if the order was filled.
        if order['avg_price'] > 0:
            price    = order['avg_price']
            notional = float(price * current_order_size)
            pnl += notional
            self.my_order.process_executed_order(current_order_size, price, now)
            print "Sold {:,} for ${:,}/share, ${:,} notional".format(current_order_size, price, notional)
            print "PnL ${:,}, Qty {:,}".format(pnl, self.my_order.get_inventory_left())
            insertNewExecutedTrade(self.trans_id, now, current_order_size, price)
        else:
            print "Unfilled order; $%s total, %s qty" % (pnl, self.my_order.get_inventory_left())

        dbsession = Session()
        trans = dbsession.query(Transactions).filter_by(username=self.username, id=self.trans_id).first()
        trans.completed = self.qty - self.my_order.get_inventory_left()
        dbsession.commit()
        dbsession.close()
        time.sleep(1)

    def __print_quotes(self):
        price = None
        for _ in xrange(TransactionExecuter.N):
            time.sleep(1)
            quote = json.loads(urllib2.urlopen(TransactionExecuter.QUERY.format(random.random())).read())
            price = float(quote['top_bid']['price'])
            print "Quoted at %s" % price
        return price

    def __clean_up_transaction(self, pnl):
        # Position is liquididated!
        print "Liquidated position for ${:,}".format(pnl)
        self.my_order.print_summary()

        dbsession = Session() 
        trans = dbsession.query(Transactions).filter_by(username=self.username, id=self.trans_id).first()
        trans.finished = True
        dbsession.commit()
        dbsession.close()
