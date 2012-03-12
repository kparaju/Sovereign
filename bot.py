from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orders import *

class IAMABot(irc.IRCClient):
    def __init__(self):
        engine = create_engine('sqlite:///sovereign.db')
        Session = sessionmaker(bind=engine)

        self.session = Session()
        # Just use the first database entry right now
        self.sovereign = self.session.query(Sovereign).first()
        self.nickname = self.sovereign.nickname.encode()

    def signedOn(self):
        for chan in self.sovereign.ircchannels:
            self.join(chan.name.encode(), chan.key.encode())

    def privmsg(self, user, channel, msg):
        order_commands = {}
        for orderset in self.sovereign.ordersets:
            order_commands["@" + orderset.name] = orderset
            order_commands["@update" + orderset.name] = orderset
        
        msgsplit = msg.split(' ')
        if (msgsplit[0] in order_commands):
            if (msgsplit[0].find('@update') != 0):
                showOrder(order_commands[msgsplit[0]], user, channel, msg)

    def showOrder(self, orderset, user, channel, msg):
        for order in orderset:
            self.msg(channel, order.encode())

    def updateOrder(self, orderset, user, channel, msg):
        msgsplit = msg.split(' ')
        number = msgsplit[1]
        territory = msgsplit[2]
        link = msgsplit[3]
        notes = msgsplit[4]
        # todo


class SovereignFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        bot = IAMABot()
        bot.factory = self
        return bot

if __name__ == '__main__':
    sovereign = SovereignFactory()
    reactor.connectTCP("irc.rizon.net", 6667, sovereign)
    reactor.run()
