USERNAME_MIN_LEN = 4
PASSWORD_MIN_LEN = 4
MAX_ORDER_SIZE = 1000000


def valid_history_date_range(start_date, end_date):
    try:
        float(start_date)
        float(end_date)
        start_date = int(start_date)
        end_date = int(end_date)
    except ValueError:
        return False
    if (start_date <= 0 or end_date <= 0):
        return False
    if (start_date > end_date):
        return False
    return True


def valid_order_parameters(quantity):
    try:
        float(quantity)
        quantity = int(quantity)
    except ValueError:
        return False

    if (type(quantity) != int):
        return False
    if (quantity is None):
        return False
    if (quantity <= 0):
        return False
    if (quantity > MAX_ORDER_SIZE):
        return False
    return True


def valid_username(username):
    if (len(username) < USERNAME_MIN_LEN):
        return False
    return True


def valid_password(password):
    if (len(password) < PASSWORD_MIN_LEN):
        return False
    return True
