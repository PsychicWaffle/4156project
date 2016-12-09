from sqlalchemy import *
from database_objects import *
import datetime as dt
import market_methods
import order

engine = None
Session = None


def createSchema():
    Base.metadata.create_all(engine)


def insertDatabaseItem(item):
    dbsession = Session()
    dbsession.add(item)
    dbsession.commit()
    dbsession.close()


def insertDatabaseItemWithId(item):
    dbsession = Session()
    dbsession.add(item)
    dbsession.flush()
    id_gen = item.id
    dbsession.commit()
    dbsession.close()
    return id_gen


def insertNewUser(username, passhash):
    new_user = UserPass(username=username, password=passhash)
    insertDatabaseItem(new_user)


def insertNewTransaction(quantity, username, order_type=0, min_price=-1):
    now = market_methods.get_market_time()
    transaction = Transactions(username=username,
                               finished=False,
                               qty_requested=quantity,
                               qty_executed=0,
                               timestamp=now,
                               queued=True,
                               order_type=order_type,
                               min_price=min_price)
    return insertDatabaseItemWithId(transaction)


def updateTransactionTradeExecuted(trans_id, qty_remaining):
    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(id=trans_id).first()
    trans.qty_executed = trans.qty_requested - qty_remaining
    dbsession.commit()
    dbsession.close()


def updateTransactionDone(trans_id):
    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(id=trans_id).first()
    trans.finished = True
    dbsession.commit()
    dbsession.close()


def updateTransactionQueuedStatus(trans_id, status):
    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(id=trans_id).first()
    trans.queued = status
    dbsession.commit()
    dbsession.close()


def insertNewExecutedTrade(trans_id, timestamp, quantity, avg_price):
    executed_trade = ExecutedTrade(trans_id=trans_id,
                                   timestamp=timestamp,
                                   quantity=quantity,
                                   avg_price=avg_price)
    return insertDatabaseItemWithId(executed_trade)


def getUser(username):
    dbsession = Session()
    user = dbsession.query(UserPass).filter_by(username=username).first()
    dbsession.close()
    return user


def removeUser(username):
    dbsession = Session()
    user = dbsession.query(UserPass).filter_by(username=username).first()
    dbsession.delete(user)
    dbsession.commit()
    dbsession.close()


def updateUserPassword(username, newpasshash):
    dbsession = Session()
    user = dbsession.query(UserPass).filter_by(username=username).first()
    user.password = newpasshash
    dbsession.commit()
    dbsession.close()


def getMaxTransactionId(username):
    dbsession = Session()
    max_id = \
        dbsession.query(func.max(Transactions.id)).\
        filter_by(username=username).first()[0]
    dbsession.close()
    return max_id


def getGroupedTransactionList(username,
                              completed=False,
                              start_date=None,
                              end_date=None,
                              date_format=None,
                              min_qty_executed=None,
                              max_qty_executed=None,
                              queued=False):
    dbsession = Session()
    grouped_trans = []
    for trans in dbsession.query(Transactions).\
            filter_by(username=username).\
            order_by(Transactions.id):
        if start_date is not None:
            if not (trans.timestamp < end_date and
                    trans.timestamp > start_date):
                continue
        if min_qty_executed is not None:
            if not trans.qty_executed >= min_qty_executed:
                continue
        if max_qty_executed is not None:
            if not trans.qty_executed <= max_qty_executed:
                continue
        if not trans.queued == queued:
            continue
        if trans.finished == completed:
            group = {'description': None, 'trans_id': None, 'sub_orders': None}
            if date_format is None:
                timestamp = \
                    str(dt.datetime.fromtimestamp(trans.timestamp).
                        strftime('%H:%M:%S'))
            else:
                timestamp = \
                    str(dt.datetime.fromtimestamp(trans.timestamp).
                        strftime(date_format))
            # print timestamp
            group['trans_id'] = trans.id
            group['sub_orders'] = []
            curr_avg_total = 0
            order_type = order.get_order_type_str(trans.order_type)
            if trans.order_type == 2:
                min_price = str(trans.min_price)
                order_type = order_type + " min price of " + min_price
            for trade in \
                    dbsession.query(ExecutedTrade).\
                    filter_by(trans_id=trans.id):
                if date_format is None:
                    timestamp = str(dt.datetime.fromtimestamp(trade.timestamp).
                                    strftime('%H:%M:%S'))
                    group['sub_orders'].append('ID: ' + str(trans.id) +
                                               ' Time: ' + timestamp +
                                               ' Qty: ' + str(trade.quantity) +
                                               ' Avg Price: ' +
                                               str(trade.avg_price))
                    curr_avg_total = curr_avg_total + (trade.quantity *
                                                       trade.avg_price)
                else:
                    timestamp = str(dt.datetime.fromtimestamp(trade.timestamp).
                                    strftime(date_format))
                    group['sub_orders'].append('ID: ' + str(trans.id) +
                                               ' Time: ' + timestamp +
                                               ' Qty: ' + str(trade.quantity) +
                                               ' Avg Price: ' +
                                               str(trade.avg_price))
                    curr_avg_total = curr_avg_total + (trade.quantity *
                                                       trade.avg_price)
            if trans.qty_executed != 0:
                total_avg = round(curr_avg_total / trans.qty_executed, 2)
                description = \
                    "%s: units requested: %d, " \
                    "executed: %d, avg price: %s %s" % \
                    (timestamp,
                     trans.qty_requested,
                     trans.qty_executed,
                     total_avg, " (" + order_type + ")")

            else:
                description = \
                    "%s: units requested: %d, executed: %d %s" % \
                    (timestamp,
                     trans.qty_requested,
                     trans.qty_executed, " (" + order_type + ")")

            group['description'] = description
            grouped_trans.append(group)
    dbsession.close()
    return grouped_trans


def getActiveTransactionList(username):
    dbsession = Session()
    trade_list = []
    for trans in dbsession.query(Transactions).\
            filter_by(username=username).\
            order_by(Transactions.id):
        if trans.finished is False:
            for trade in dbsession.query(ExecutedTrade).\
                    order_by(ExecutedTrade.timestamp).\
                    filter_by(trans_id=trans.id):
                trade_list.append('ID: ' + str(trans.id) +
                                  ' Time: ' +
                                  str(dt.datetime.
                                      fromtimestamp(trade.timestamp).
                                      strftime('%H:%M:%S')) +
                                  ' Qty: ' + str(trade.quantity) +
                                  ' Avg Price: ' + str(trade.avg_price))
    dbsession.close()
    return trade_list


def getTransactionById(tid):
    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(id=tid).first()
    dbsession.close()
    return trans


def getActiveTransactions(username):
    dbsession = Session()
    transactions = []
    for trans in dbsession.query(Transactions).\
            filter_by(username=username).\
            order_by(Transactions.id):
        if trans.finished is False:
            transactions.append(trans)
    dbsession.close()
    return transactions


def removeTransactionsByUsername(username):
    dbsession = Session()
    for trans in dbsession.query(Transactions).\
            filter_by(username=username).\
            order_by(Transactions.id):
        dbsession.delete(trans)
        dbsession.commit()
    dbsession.close()


def removeExecutedTradesById(tid):
    dbsession = Session()
    for item in dbsession.query(ExecutedTrade).\
            filter_by(trans_id=tid).\
            order_by(ExecutedTrade.trans_id):
        dbsession.delete(item)
        dbsession.commit()
    dbsession.close()


def removeTransactionsById(tid):
    dbsession = Session()
    for trans in dbsession.query(Transactions).\
            filter_by(id=tid).\
            order_by(Transactions.id):
        dbsession.delete(trans)
        dbsession.commit()
    dbsession.close()


def getAllTransactionList(username):
    dbsession = Session()
    trans_list = []
    for trans in dbsession.query(Transactions).\
            filter_by(username=username).\
            order_by(Transactions.id):
        trans_list.append(trans)
    dbsession.close()
    return trans_list
