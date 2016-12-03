from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserPass(Base):
    __tablename__ = 'userpass'
    # id = Column(Integer, primary_key=True)
    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)

    def __repr__(self):
        return "<UserPass(username='%s', password='%s')>" % (self.username,
                                                             self.password)


class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('userpass.username'))
    qty_requested = Column(Integer, nullable=False)
    qty_executed = Column(Integer, nullable=False)
    timestamp = Column(Integer, nullable=False)
    finished = Column(Boolean, nullable=False)
    queued = Column(Boolean, nullable=False)
    order_type = Column(Integer, nullable=False)
    min_price = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Transactions(username='%s', id='%d')>" % (self.username,
                                                           self.id)


class ExecutedTrade(Base):
    __tablename__ = 'executedtrade'
    id = Column(Integer, primary_key=True)
    trans_id = Column(Integer, ForeignKey('transactions.id'))
    timestamp = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)

    def __repr__(self):
        return "<ExecutedTrades(trans_id='%d', timestamp='%d')>" % \
            (self.id, self.timestamp)
