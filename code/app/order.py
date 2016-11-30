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
    min_order_window = 500
    min_order_size = 5
    last_order_cushion = 1800
    
    def __init__(self, initial_inventory, start_time, min_price=None, max_time=None, order_type=None):
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory
        self.executed_trades = []
        self.min_price = min_price
        self.max_time = max_time
        self.next_order_time = start_time
        self.next_order_size = 0
        self.order_type = order_type
        if (max_time != None):
            self.expiration_time = start_time + max_time
        else:
            self.expiration_time = market_methods.get_end_of_day_time()
        self.__set_next_order(first_order=True)
        if (self.__check_valid_order() == False):
            raise ValueError('Invalid order created')

    def get_next_order(self):
        if (self.order_type == 2):
            curr_price = self.__get_current_market_price() 
            if (curr_price < self.min_price):
                return (None, None)
        order_size = self.__get_next_order_size()
        order_time = self.__get_next_order_time()
        return (order_size, order_time)

    def __get_next_order_size(self):
        return int(self.next_order_size)
            
    def __set_next_order(self, first_order=False):
        curr_time = self.__get_current_market_time()
        seconds_left = self.__time_left_to_complete_order()
        print "seconds left %d" % seconds_left
        cushioned_seconds_left = seconds_left - self.last_order_cushion
        if (self.order_type == 1):
            self.next_order_size = self.curr_inventory
            self.next_order_time = curr_time - 10
            return
        qty_multiplier = 1.0
        curr_inventory = self.curr_inventory
        if (curr_inventory > 0):
            curr_window = float(cushioned_seconds_left) / float(curr_inventory)
            found_next_order = False
        else:
            found_next_order = True

        while (found_next_order == False):
            #print "cushioned secs %d" % cushioned_seconds_left
            #print "inven %d" % curr_inventory
            curr_window = (qty_multiplier * float(cushioned_seconds_left)) / float(curr_inventory)
            #print "curr window %d" % int(curr_window)
            if (curr_window >= self.min_order_window):
                self.next_order_time = curr_time + curr_window
                self.next_order_size = 1 * int(qty_multiplier)
                found_next_order = True
            else:
                qty_multiplier = qty_multiplier + 1.0

        if (self.next_order_size >= self.curr_inventory):
            self.next_order_size = self.curr_inventory

        if (first_order == True):
            self.next_order_time = curr_time

        #print "curr time %d" % curr_time
        #print "next time %d" % self.next_order_time
        #print "next size %d" % self.next_order_size
    def __get_next_order_time(self):
        if (self.order_type == 1):
            curr_time = self.__get_current_market_time() 
            if (self.next_order_time > curr_time):
                self.next_order_time = curr_time
            return self.next_order_time

        return self.next_order_time

    def process_executed_order(self, quantity, avg_price, time):
        self.executed_trades.append({ 'quantity' : quantity, 'avg_price' :  avg_price, 'time' : time })
        self.curr_inventory -= quantity
        time_left_to_complete = self.__time_left_to_complete_order
        self.__set_next_order()
        self.next_order_time += 10
        return 1

    def get_inventory_left(self):
        return self.curr_inventory

    def get_executed_trades(self):
        return self.executed_trades

    def __get_current_market_price(self):
        price = market_methods.get_market_price()
        return price

    def __get_current_market_time(self):
        time = market_methods.get_market_time()
        return time

    def __time_left_in_day(self):
        curr_time = self.__get_current_market_time() 
        closing_time = self.__market_closing_time()
        return closing_time - curr_time

    def __time_left_to_complete_order(self):
        curr_time = self.__get_current_market_time()
        print "curr time %d" % curr_time
        print "expo time %d" % self.expiration_time
        return self.expiration_time - curr_time
            
    def __market_closing_time(self):
        closing_time_str = "2016-11-21 08:30:00.090257"
        t = datetime.datetime.strptime(closing_time_str, "%Y-%m-%d %H:%M:%S.%f");
        closing_time_seconds = time.mktime(t.timetuple())
        print "closing time in secs %d" % closing_time_seconds
        return closing_time_seconds

    def __market_price_below_min():
        if (self.min_price == None):
            return False
        else:
            curr_price = curr_time = self.__get_current_market_price()
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
