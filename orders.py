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
    nickservpwd = Column(String)

    ordersets = relationship('OrderSet', order_by='OrderSet.id', backref='sovereign')
    ircchannels = relationship('IRCChannel', order_by='IRCChannel.name', backref='sovereign')
    ircusers = relationship('IRCUser', order_by='IRCUser.nick', backref='sovereign')

    def __init__(self, nickname):
        self.nickname = nickname


class IRCUser(Base):
    __tablename__ = 'ircusers'
    id = Column(Integer, Sequence('ircuser_id_seq'), primary_key=True)

    nick = Column(String)
    admin = Column(Boolean)
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))

    def __init__(self, nick):
        self.nick = nick
        self.admin = False

    def __repr__(self):
        return "<IRCUser ('%s','%s')>" % (self.nick, self.admin)


class IRCChannel(Base):
    __tablename__ = 'ircchannels'
    id = Column(Integer, Sequence('ircchannel_id_seq'), primary_key=True)
    name = Column(String)
    key = Column(String)
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))
    autojoin = Column(Boolean)

    def __init__(self, name, key=''):
        if ((name.find("#") != 0) & (len(name) < 2)):
            raise Exception("Invalid channel name")

        self.name = name
        self.key = key
        self.autojoin = True

    def __repr__(self):
        return "<IRCChannel ('%s', '%s')>" % (self.name, self.key)


orderset_authorized_channels_table = Table('orderset_authorized_channels', Base.metadata,
    Column('orderset_id', Integer, ForeignKey('ordersets.id')),
    Column('ircchannel_id', Integer, ForeignKey('ircchannels.id'))
)

orderset_authorized_users_table = Table('orderset_authorized_users', Base.metadata,
    Column('orderset_id', Integer, ForeignKey('ordersets.id')),
    Column('ircusers_id', Integer, ForeignKey('ircusers.id'))
)

class OrderSet(Base):
    __tablename__ = 'ordersets'

    id = Column(Integer, Sequence('orderset_id_seq'), primary_key=True)
    name = Column(String)
    orders = relationship('Order', order_by='Order.id', backref='orderset')
    sovereign_id = Column(Integer, ForeignKey('sovereign.id'))
    authorized_channels = relationship("IRCChannel", secondary=orderset_authorized_channels_table,
        backref="ordersets")
    admins = relationship("IRCUser", secondary=orderset_authorized_users_table, backref= "ordersets")


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




