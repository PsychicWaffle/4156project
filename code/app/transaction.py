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
import json
import random
import py_compile
from order import Order
from database_objects import *
from database_methods import *
import datetime
import market_methods
import time

class TransactionExecuter:
    # Server API URLs
    QUERY = "http://localhost:8080/query?id={}"
    ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"
    ORDER_DISCOUNT = 10
    BACK_ON_QUEUE_TIME_FRAME=60
    N = 5

    def __init__(self, username, trans_id):
        self.username = username
        self.trans_id = trans_id
        self.my_order = None
        if (self.check_valid_transaction() == False):
            raise ValueError('Invalid transaction parameters')

    def execute_transaction(self, my_order):
        '''
        Execute a transaction for a givent amount of inventory
        Method used from given sample in client.py
        '''
        # Start with all shares and no profit
        pnl = 0
        start_time = market_methods.get_market_time()
        self.my_order = my_order

        recalculate_next_order = False
        # Repeat the strategy until we run out of shares.
        while (self.my_order.get_inventory_left() > 0):
            price = self.__print_quotes()
            if (price == -1):
                time.sleep(3)
                continue
            now = market_methods.get_market_time()
            if recalculate_next_order == True:
                current_order_size, current_order_time = self.my_order.get_next_order(recalc=True)
                recalculate_next_order = False
            else:
                current_order_size, current_order_time = self.my_order.get_next_order()

            if (current_order_size == None or current_order_time == None):
                recalculate_next_order = True
                continue
            if now < current_order_time:
                if (current_order_time - now > TransactionExecuter.BACK_ON_QUEUE_TIME_FRAME):
                    time_str = datetime.datetime.fromtimestamp(current_order_time).strftime("%Y-%m-%d %H:%M:%S")
                    print "Too long until next time so putting self back on queue!"
                    print "Next order time: %s" % time_str
                    print "Next order size: %d" % current_order_size
                    remaining_qty_to_fill = self.my_order.get_inventory_left
                    return remaining_qty_to_fill
                else:
                    continue
            else:
                self.__attempt_to_execute_sub_order(current_order_size, current_order_time, price, pnl, now)

        self.__clean_up_transaction(pnl)
        return 0

    def __attempt_to_execute_sub_order(self, current_order_size, current_order_time, price, pnl, now):
        # Attempt to execute a sell order.
        order_args = (current_order_size, price - TransactionExecuter.ORDER_DISCOUNT)
        print "Executing 'sell' of {:,} @ {:,}".format(*order_args)
        url = TransactionExecuter.ORDER.format(random.random(), *order_args)
        executed_sub_order = False
        original_order_size = current_order_size
        order_size_completed = 0
        total_attempts_to_execute_sub_order = 0
        attempts_to_execute_sub_order = 0
        while (executed_sub_order == False):
            attempts_to_execute_sub_order = attempts_to_execute_sub_order + 1
            total_attempts_to_execute_sub_order = total_attempts_to_execute_sub_order + 1
            try: 
                order = json.loads(urllib2.urlopen(url).read())
                qty_filled = order['qty']
                order_size_completed = order_size_completed + qty_filled
                self.__process_filled_suborder(order, pnl, now);
                if (order_size_completed < original_order_size):
                    order_size_left = original_order_size - order_size_completed
                    order_args = (order_size_left, price - TransactionExecuter.ORDER_DISCOUNT)
                    url = TransactionExecuter.ORDER.format(random.random(), *order_args)
                    attempts_to_execute_sub_order = 0
                else:
                    executed_sub_order = True
            except ValueError:
                print 'Failed to get quote from exchange'
                if (total_attempts_to_execute_sub_order > 10):
                    time.sleep(total_attempts_to_execute_sub_order / 10)
                if (attempts_to_execute_sub_order > 3):
                    current_order_size = current_order_size / 2
                    if (current_order_size == 0):
                        current_order_size = 1
                    order_args = (current_order_size, price - TransactionExecuter.ORDER_DISCOUNT)
                    url = TransactionExecuter.ORDER.format(random.random(), *order_args)
                    print "Lowering order size, now executing 'sell' of {:,} @ {:,}".format(*order_args)
                    attempts_to_execute_sub_order = 0
                continue

    def __process_filled_suborder(self, order, pnl, now):
        # Update the PnL if the order was filled.
        if order['avg_price'] > 0:
            price = order['avg_price']
            qty = order['qty']
            notional = float(price * qty)
            pnl += notional
            self.my_order.process_executed_order(qty, price, now)
            print "Sold {:,} for ${:,}/share, ${:,} notional".format(qty, price, notional)
            print "PnL ${:,}, Qty {:,}".format(pnl, self.my_order.get_inventory_left())
            # insert the executed trade into the database
            insertNewExecutedTrade(self.trans_id, now, qty, price)
        else:
            print "Unfilled order; $%s total, %s qty" % (pnl, self.my_order.get_inventory_left())
        # update the transaction in db for executed trade
        updateTransactionTradeExecuted(self.trans_id, self.my_order.get_inventory_left())
        time.sleep(1)

    def __clean_up_transaction(self, pnl):
        # Position is liquididated!
        print "Liquidated position for ${:,}".format(pnl)
        self.my_order.print_summary()
        # mark the transaction as completed in the database
        updateTransactionDone(self.trans_id)

    def __print_quotes(self):
        price = None
        for _ in xrange(TransactionExecuter.N):
            time.sleep(0.1)
            price = market_methods.get_market_price()
            if (price == -1):
                return -1
            print "Quoted at %s" % price

        return price

    def check_valid_transaction(self):
        return True
