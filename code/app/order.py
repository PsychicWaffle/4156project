import py_compile
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 3600
HOURS_IN_DAY = 24

class Order:

    def __init__(self, initial_inventory, start_time):
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory
        self.next_order_time = start_time

    def get_next_order(self):
        order_size = self.get_next_order_size()
        order_time = self.get_next_order_time()
        return (order_size, order_time)

    def get_next_order_size(self):
        order_size = self.initial_inventory / 24
        return int(order_size)
    
    def get_next_order_time(self):
        return self.next_order_time

    def process_executed_order(self):
        self.curr_inventory -= self.get_next_order_size()
        self.next_order_time += SECONDS_IN_MINUTE / 2

    def get_inventory_left(self):
        return self.curr_inventory

    def print_current_order(self):
        print "Initial inventory: %d" % self.initial_inventory
        print "Current inventory: %d" % self.curr_inventory
