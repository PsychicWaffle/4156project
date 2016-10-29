from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from database_objects import *
import datetime as dt

DATABASE_URI = "postgresql://localhost/users"
engine = create_engine(DATABASE_URI)
# # for in memory database
# engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)

def createSchema():
	Base.metadata.create_all(engine)

def getUser(username):
	dbsession = Session()
	user = dbsession.query(UserPass).filter_by(username=username).first()
	dbsession.close()
	return user

def createNewUser(username, passhash):
	dbsession = Session()
	new_user = UserPass(username=username, password=passhash)
	dbsession.add(new_user)
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

def insertTransaction(transaction):
	dbsession = Session()
	dbsession.add(transaction)
	dbsession.commit()
	dbsession.close()

def getActiveTransactionList(username):
	dbsession = Session()
	trade_list = []
	for trans in dbsession.query(Transactions).filter_by(username=username).order_by(Transactions.id):
		if trans.finished is False:
			for trade in dbsession.query(ExecutedTrade).order_by(ExecutedTrade.timestamp).filter_by(transaction_id=trans.id, username=username):
				trade_list.append('ID: ' + str(trans.id) + ' Time: ' + str(dt.datetime.fromtimestamp(trade.timestamp).strftime('%H:%M:%S')) + ' Qty: ' + str(trade.quantity) + ' Avg Price: ' + str(trade.avg_price))
	dbsession.close()
	return trade_list