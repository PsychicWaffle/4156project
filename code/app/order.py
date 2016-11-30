import py_compile
import market_methods
import time
import datetime

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
HOURS_IN_DAY = 24

min_order_size = 1

# order type -> 0 = regular order 1-> market order

class Order:

    lower_end_price = 70
    higher_end_price = 160
    
    def __init__(self, initial_inventory, start_time, min_price=None, max_time=None, order_type=None):
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory
        self.next_order_time = start_time
        self.executed_trades = []
        self.min_price = min_price
        self.max_time = max_time
        self.order_type = order_type
        if (max_time != None):
            self.expiration_time = start_time + max_time
        else:
            self.expiration_time = self.__market_closing_time()
        if (self.__check_valid_order() == False):
            raise ValueError('Invalid order created')

    def get_next_order(self):
        order_size = self.__get_next_order_size()
        order_time = self.__get_next_order_time()
        return (order_size, order_time)

    def __get_next_order_size(self):
        # order_size = self.initial_inventory / 24
        if (self.order_type == 1):
            order_size = self.curr_inventory
            return int(order_size)

        order_size = self.initial_inventory / 10
        if order_size < min_order_size:
            order_size = min_order_size

        if (order_size >= self.curr_inventory):
            return self.curr_inventory

        return int(order_size)
    
    def __get_next_order_time(self):
        if (self.order_type == 1):
            curr_time = self.__get_curret_market_time() 
            if (self.next_order_time > curr_time):
                self.next_order_time = curr_time
            return self.next_order_time

        return self.next_order_time

    def process_executed_order(self, quantity, avg_price, time):
        self.executed_trades.append({ 'quantity' : quantity, 'avg_price' :  avg_price, 'time' : time })
        self.curr_inventory -= quantity
        time_left_to_complete = self.__time_left_to_complete_order
        self.next_order_time += 10
        return 1

    def get_inventory_left(self):
        return self.curr_inventory

    def get_executed_trades(self):
        return self.executed_trades

    def __get_current_market_price(self):
        price = market_methods.get_market_price()
        return price

    def __get_curret_market_time(self):
        time = market_methods.get_market_time()
        return time

    def __time_left_in_day(self):
        curr_time = self.__get_curret_market_time() 
        closing_time = self.__market_closing_time()
        return closing_time - curr_time

    def __time_left_to_complete_order(self):
        curr_time = self.__get_curret_market_time()
        return self.expiration_time - curr_time
            
    def __market_closing_time(self):
        closing_time_str = "2016-11-21 08:30:00.090257"
        t = datetime.datetime.strptime(closing_time_str, "%Y-%m-%d %H:%M:%S.%f");
        closing_time_seconds = time.mktime(t.timetuple())
        return closing_time_seconds

    def __market_price_below_min():
        if (self.min_price == None):
            return False
        else:
            curr_price = curr_time = self.__get_curret_market_price()
            if (curr_price < self.min_price):
                return True
            else:
                return False

    def __check_valid_order(self):
        if (self.initial_inventory < 0):
            return False
        if (self.start_time < 0):
            return False
        return True

    def print_current_order(self):
        print "Initial inventory: %d" % self.initial_inventory
        print "Current inventory: %d" % self.curr_inventory

    def print_summary(self):
        print "Initial inventory: %d" % self.initial_inventory
        print "Printing Order Summary:"
        for trade in self.get_executed_trades():
            print "{ qt: %d , avg_price: %f, trade_time: %s }" % (trade['quantity'], trade['avg_price'], time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(trade['time'])))
