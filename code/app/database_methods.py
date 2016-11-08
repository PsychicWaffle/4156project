from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from database_objects import *
import datetime as dt

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

def insertNewTransaction(quantity, username):
	transaction = Transactions(username=username, finished=False, qty_requested=quantity, qty_executed=0)
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

def insertNewExecutedTrade(trans_id, timestamp, quantity, avg_price):
	executed_trade = ExecutedTrade(trans_id=trans_id, timestamp=timestamp, quantity=quantity, avg_price=avg_price)
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
	max_id = dbsession.query(func.max(Transactions.id)).filter_by(username=username).first()[0]
	dbsession.close()
	return max_id


def getActiveTransactionList(username):
	dbsession = Session()
	trade_list = []
	for trans in dbsession.query(Transactions).filter_by(username=username).order_by(Transactions.id):
		if trans.finished is False:
			for trade in dbsession.query(ExecutedTrade).order_by(ExecutedTrade.timestamp).filter_by(trans_id=trans.id):
				trade_list.append('ID: ' + str(trans.id) + ' Time: ' + str(dt.datetime.fromtimestamp(trade.timestamp).strftime('%H:%M:%S')) + ' Qty: ' + str(trade.quantity) + ' Avg Price: ' + str(trade.avg_price))
	dbsession.close()
	return trade_list

def getTransactionById(id):
	dbsession = Session()
        trans = dbsession.query(Transactions).filter_by(id=id).first()
	dbsession.close()
        return trans

def removeTransactionsByUsername(username):
        dbsession = Session()
	for trans in dbsession.query(Transactions).filter_by(username=username).order_by(Transactions.id):
            dbsession.delete(trans)
            dbsession.commit()
	dbsession.close()

def removeExecutedTradesById(id):
        dbsession = Session()
        for item in dbsession.query(ExecutedTrade).filter_by(trans_id=id).order_by(ExecutedTrade.trans_id):
            dbsession.delete(item)
            dbsession.commit()
	dbsession.close()

def removeTransactionsById(id):
        dbsession = Session()
	trans_list = []
	for trans in dbsession.query(Transactions).filter_by(id=id).order_by(Transactions.id):
            dbsession.delete(trans)
            dbsession.commit()
	dbsession.close()

def getAllTransactionList(username):
        dbsession = Session()
	trans_list = []
	for trans in dbsession.query(Transactions).filter_by(username=username).order_by(Transactions.id):
            trans_list.append(trans)
	dbsession.close()
	return trans_list
