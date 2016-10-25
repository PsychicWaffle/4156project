from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URI = "postgresql://localhost/users"
engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class UserPass(Base):
    __tablename__ = 'userpass'
    # id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, primary_key=True)
    password = Column(String, nullable=False)

    def __repr__(self):
        return "<UserPass(username='%s', password='%s')>" % (self.username, self.password)

class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('userpass.username'), primary_key=True)
    completed = Column(Integer)
    finished = Column(Boolean)

    def __repr__(self):
        return "<Transactions(username='%s', id='%d')>" % (self.username, self.id)

class ExecutedTrade(Base):
    __tablename__ = 'executedtrade'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer)
    username = Column(String)
    timestamp = Column(Integer)
    quantity = Column(Integer)
    avg_price = Column(Float)

    def __repr__(self):
        return "<ExecutedTrades(trans_id='%d', timestamp='%d')>" % (self.id, self.timestamp)

