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
        if (self.check_valid_transaction() == False):
            raise ValueError('Invalid transaction parameters')

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
            if (price == -1):
                time.sleep(3)
                continue

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
        executed_sub_order = False
        attempts_to_execute_sub_order = 0
        while (executed_sub_order == False):
            attempts_to_execute_sub_order = attempts_to_execute_sub_order + 1
            try: 
                order = json.loads(urllib2.urlopen(url).read())
                executed_sub_order = True
            except ValueError:
                print 'Failed to get quote from exchange'
                if (attempts_to_execute_sub_order > 3):
                    current_order_size = current_order_size / 2
                    if (current_order_size == 0):
                        current_order_size = 1
                    order_args = (current_order_size, price - TransactionExecuter.ORDER_DISCOUNT)
                    url = TransactionExecuter.ORDER.format(random.random(), *order_args)
                    print "Lowering order size, now executing 'sell' of {:,} @ {:,}".format(*order_args)
                    attempts_to_execute_sub_order = 0
                continue

        # Update the PnL if the order was filled.
        if order['avg_price'] > 0:
            price    = order['avg_price']
            notional = float(price * current_order_size)
            pnl += notional
            self.my_order.process_executed_order(current_order_size, price, now)
            print "Sold {:,} for ${:,}/share, ${:,} notional".format(current_order_size, price, notional)
            print "PnL ${:,}, Qty {:,}".format(pnl, self.my_order.get_inventory_left())
            # insert the executed trade into the database
            insertNewExecutedTrade(self.trans_id, now, current_order_size, price)
        else:
            print "Unfilled order; $%s total, %s qty" % (pnl, self.my_order.get_inventory_left())
        # update the transaction in db for executed trade
        updateTransactionTradeExecuted(self.trans_id, self.my_order.get_inventory_left())
        time.sleep(1)

    def __print_quotes(self):
        price = None
        for _ in xrange(TransactionExecuter.N):
            time.sleep(1)
            try:
                quote = json.loads(urllib2.urlopen(TransactionExecuter.QUERY.format(random.random())).read())
            except ValueError:
                print 'Failed to get quote from exchange'
                return -1

            price = float(quote['top_bid']['price'])
            print "Quoted at %s" % price
        return price

    def __clean_up_transaction(self, pnl):
        # Position is liquididated!
        print "Liquidated position for ${:,}".format(pnl)
        self.my_order.print_summary()
        # mark the transaction as completed in the database
        updateTransactionDone(self.trans_id)

    def check_valid_transaction(self):
        if (self.qty == False):
            return False
        return True
