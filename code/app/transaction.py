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
from database import *

# Server API URLs
QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"

# Strategy config.  We will attempt to liquidate a position of INVENTORY shares,
# by selling ORDER_SIZE @ top_bid - ORDER_DISCOUNT, once every N seconds.
ORDER_DISCOUNT = 10
#ORDER_SIZE     = 200

N = 5

def execute_transaction(INVENTORY, username, trans_id):
    '''
    Execute a transaction for a givent amount of inventory
    Method used from given sample in client.py
    '''
    # Start with all shares and no profit
    qty = INVENTORY
    pnl = 0
    start_time = time.time()
    print "start time %d" % start_time
    my_order = Order(INVENTORY, start_time)

    # Repeat the strategy until we run out of shares.
    while my_order.get_inventory_left() > 0:

        my_order.print_current_order()
        # Query the price once every N seconds.
        for _ in xrange(N):
            time.sleep(1)
            quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
            price = float(quote['top_bid']['price'])
            print "Quoted at %s" % price

            now = time.time()

            current_order_size, current_order_time = my_order.get_next_order()
            # print type(next_order)
            if now < current_order_time:
                continue

        # Attempt to execute a sell order.
        order_args = (current_order_size, price - ORDER_DISCOUNT)
        print "Executing 'sell' of {:,} @ {:,}".format(*order_args)
        url   = ORDER.format(random.random(), *order_args)
        order = json.loads(urllib2.urlopen(url).read())

        # Update the PnL if the order was filled.
        if order['avg_price'] > 0:
            price    = order['avg_price']
            notional = float(price * current_order_size)
            pnl += notional
            my_order.process_executed_order(current_order_size, price, now)
            print "Sold {:,} for ${:,}/share, ${:,} notional".format(current_order_size, price, notional)
            print "PnL ${:,}, Qty {:,}".format(pnl, my_order.get_inventory_left())
        else:
            print "Unfilled order; $%s total, %s qty" % (pnl, my_order.get_inventory_left())

        dbsession = Session()
        trans = dbsession.query(Transactions).filter_by(username=username, id=trans_id).first()
        trans.completed = qty - my_order.get_inventory_left()
        dbsession.commit()
        dbsession.close()
        time.sleep(1)

    # Position is liquididated!
    print "Liquidated position for ${:,}".format(pnl)
    print my_order.print_summary()
    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(username=username, id=trans_id).first()
    trans.finished = True
    dbsession.commit()
    dbsession.close()
