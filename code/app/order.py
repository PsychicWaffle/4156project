import py_compile
import time

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
HOURS_IN_DAY = 24

min_order_size = 1

class Order:

    def __init__(self, initial_inventory, start_time):
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory
        self.next_order_time = start_time
        self.executed_trades = []

    def get_next_order(self):
        order_size = self.get_next_order_size()
        order_time = self.get_next_order_time()
        return (order_size, order_time)

    def get_next_order_size(self):
        # order_size = self.initial_inventory / 24
        order_size = self.initial_inventory / 10
        if order_size < min_order_size:
            order_size = min_order_size

        return int(order_size)
    
    def get_next_order_time(self):
        return self.next_order_time

    def process_executed_order(self, quantity, avg_price, time):
        self.executed_trades.append({ 'quantity' : quantity, 'avg_price' :  avg_price, 'time' : time })
        self.curr_inventory -= quantity
        self.next_order_time += 10

    def get_inventory_left(self):
        return self.curr_inventory

    def get_executed_trades(self):
        return self.executed_trades

    def print_current_order(self):
        print "Initial inventory: %d" % self.initial_inventory
        print "Current inventory: %d" % self.curr_inventory

    def print_summary(self):
        print "Initial inventory: %d" % self.initial_inventory
        print "Printing Order Summary:"
        for trade in self.get_executed_trades():
            print "{ qt: %d , avg_price: %f, trade_time: %s }" % (trade['quantity'], trade['avg_price'], time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(trade['time'])))
