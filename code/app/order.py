import py_compile
import market_methods
import time
import datetime

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 1800
HOURS_IN_DAY = 24

min_order_size = 1

class Order:

    lower_end_price = 70
    higher_end_price = 160
    last_order_cushion = 3600
    qty_threshold = 500
    min_window_size = 500

    def __init__(self,
                 initial_inventory,
                 start_time,
                 min_price=None,
                 order_type=None):
        self.order_window = 500
        self.min_order_size = 5
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory
        self.executed_trades = []
        self.min_price = min_price
        self.next_order_time = start_time
        self.next_order_size = 0
        self.order_type = order_type
        self.expiration_time = market_methods.get_end_of_day_time()
        self.__set_next_order(first_order=True)
        if (self.__check_valid_order() is False):
            raise ValueError('Invalid order created')

    def get_next_order(self, recalc=False):
        if (self.order_type == 2):
            curr_price = self.__get_current_market_price()
            if (curr_price < self.min_price):
                curr_time = self.__get_current_market_time()
                if (self.__get_next_order_time() < curr_time):
                    self.__set_next_order(first_order=True)
                return (None, None)
            else:
                if recalc is True:
                    self.__set_next_order(first_order=True)

        order_size = self.__get_next_order_size()
        order_time = self.__get_next_order_time()
        return (order_size, order_time)

    def __get_next_order_size(self):
        return int(self.next_order_size)

    def __set_next_order(self, first_order=False):
        curr_time = self.__get_current_market_time()
        seconds_left = self.__time_left_to_complete_order()
        cushioned_seconds_left = seconds_left - self.last_order_cushion
        if cushioned_seconds_left <= 0:
            self.next_order_size = self.curr_inventory
            self.next_order_time = curr_time
            return

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

        while (found_next_order is False):
            # print "cushioned secs %d" % cushioned_seconds_left
            # print "inven %d" % curr_inventory
            curr_window = ((qty_multiplier *
                           float(cushioned_seconds_left)) /
                           float(curr_inventory))
            # print "curr window %d" % int(curr_window)
            if (curr_window >= self.order_window):
                self.next_order_time = curr_time + curr_window
                self.next_order_size = 1 * int(qty_multiplier)
                found_next_order = True
            else:
                qty_multiplier = qty_multiplier + 1.0

        while (self.next_order_size > 500):
            curr_time_to_next_order_time = self.next_order_time - curr_time
            if (not curr_time_to_next_order_time < 20):
                self.next_order_size = int(float(self.next_order_size) / 2.0)
                self.next_order_time = \
                    self.next_order_time - \
                    int((float(curr_time_to_next_order_time) / 2.0))
            else:
                break

        increased_due_to_price = False
        curr_price = self.__get_current_market_price()
        if (curr_price >= 140):
            self.next_order_size = int(float(self.next_order_size) * 2)
            increased_due_to_price = True
        else:
            if (curr_price >= 130):
                self.next_order_size = int(float(self.next_order_size) * 1.5)
                increased_due_to_price = True
            else:
                if (curr_price >= 120):
                    self.next_order_size = int(float(self.next_order_size) * 1.2)
                    increased_due_to_price = True

        if increased_due_to_price is True:
            while (self.next_order_size > 500):
                curr_time_to_next_order_time = self.next_order_time - curr_time
                if (not curr_time_to_next_order_time < 5):
                    self.next_order_size = \
                        int(float(self.next_order_size) / 2.0)
                    self.next_order_time = \
                        self.next_order_time - \
                        int((float(curr_time_to_next_order_time) / 2.0))
                else:
                    break

        if (self.next_order_size >= self.curr_inventory):
            self.next_order_size = self.curr_inventory

        if (first_order is True):
            self.next_order_time = curr_time - 10

    def __get_next_order_time(self):
        if (self.order_type == 1):
            curr_time = self.__get_current_market_time()
            if (self.next_order_time > curr_time):
                self.next_order_time = curr_time
            return self.next_order_time

        return self.next_order_time

    def process_executed_order(self,
                               quantity,
                               avg_price,
                               time,
                               still_executing=False):
        self.executed_trades.append({'quantity': quantity,
                                     'avg_price':  avg_price,
                                     'time': time})
        self.curr_inventory -= quantity
        if (still_executing is False):
            self.__set_next_order()
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

    def __time_left_to_complete_order(self):
        curr_time = self.__get_current_market_time()
        return self.expiration_time - curr_time

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
            print "{ qt: %d , avg_price: %f, trade_time: %s }" % \
                  (trade['quantity'],
                   trade['avg_price'],
                   time.strftime("%Y-%m-%d %H:%M:%S",
                                 time.gmtime(trade['time'])))


def get_order_type_str(o):
    if o == 0:
        return "Time-weighted"
    if o == 1:
        return "Market"
    if o == 2:
        return "Limit"
    raise ValueError('Unknown order type')
