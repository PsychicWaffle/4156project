import py_compile

class Order:

    def __init__(self, initial_inventory, start_time):
        self.initial_inventory = initial_inventory
        self.start_time = start_time
        self.curr_inventory = self.initial_inventory

    def get_next_order_size(self, curr_time):
        order_size = self.initial_inventory / 24
        return int(order_size)

    def reduce_curr_investory(self, amount):
        self.curr_inventory -= amount

    def get_inventory_left(self):
        return self.curr_inventory
