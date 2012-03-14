
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from orders import *
from sqlalchemy.orm import sessionmaker
import os.path

engine = create_engine('sqlite:///sovereign.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

if (not os.path.isfile("sovereign.db")):
    Base.metadata.create_all(engine)

    s = Sovereign("Sovereign-Beta")
    s.serverhost = "irc.rizon.net"
    s.serverport = 6667
    s.serverpass = ""
    c = IRCChannel("#sovereign-beta")
    s.ircchannels.append(c)

    os = OrderSet("home")
    order_1 = Order("t","u","info")
    order_2 = Order("t__2","u_2","info_2")
    os.orders.append(order_1)
    os.orders.append(order_2)

    s.ordersets.append(os)

    session.add(s)
    session.commit()

    bot = session.query(Sovereign).first()
    for chan in bot.ircchannels:
        print chan.name + " " + chan.key
else:
    bot = session.query(Sovereign).first()

