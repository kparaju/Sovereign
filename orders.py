import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Sovereign(Base):
    __tablename__ = 'sovereign'

    id = Column(Integer, Sequence('sovereign_id_seq'), primary_key=True)

    nickname = Column(String)
    serverpass = Column(String)
    serverhost = Column(String)
    serverport = Column(Integer)

    ordersets = relationship('OrderSet', order_by='OrderSet.id', backref='sovereign')
    ircchannels = relationship('IRCChannel', order_by='IRCChannel.name', backref='sovereign')
    ircusers = relationship('IRCUser', order_by='IRCUser.nick', backref='sovereign')

    def __init__(self, nickname):
        self.nickname = nickname


class IRCUser(Base):
    __tablename__ = 'user'
    nick = Column(String, primary_key=True)
    admin = Column(Boolean)
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))

    def __init__(self, nick):
        self.nick = nick

    def __repr__(self):
        return "<IRCUser ('%s','%s')>" % (self.nick, self.admin)


class IRCChannel(Base):
    __tablename__ = 'ircchannels'
    name = Column(String, primary_key=True)
    key = Column(String)
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))

    def __init__(self, name, key=''):
        self.name = name
        self.key = key

    def __repr__(self):
        return "<IRCChannel ('%s', '%s')>" % (self.name, self.key)


class OrderSet(Base):
    __tablename__ = 'ordersets'

    id = Column(Integer, Sequence('orderset_id_seq'), primary_key=True)
    name = Column(String)
    orders = relationship('Order', order_by='Order.id', backref='orderset')
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<OrderSet %s: %s>" % (self.name, self.orders)


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, Sequence('order_id_seq'), primary_key=True)
    territory = Column(String)
    url = Column(String)
    info = Column(String)

    orderset_id = Column(Integer, ForeignKey('ordersets.id'))


    def __init__(self, territory, url, info):
        self.territory = territory
        self.url = url
        self.info = info

    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (self.territory, self.url, self.info)




