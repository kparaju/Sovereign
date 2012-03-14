from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orders import *
from messagehandler import *

class IAMABot(irc.IRCClient):
    def __init__(self):
        engine = create_engine('sqlite:///sovereign.db')
        Session = sessionmaker(bind=engine)

        self.session = Session()
        self.sovereign = self.session.query(Sovereign).first()
        self.nickname = self.sovereign.nickname.encode()
        self.password = self.sovereign.serverpass.encode()

    def signedOn(self):
        for chan in self.sovereign.ircchannels:
            self.join(chan.name.encode(), chan.key.encode())

    def privmsg(self, user, channel, msg):

        try:
            message_handler = SovereignMessageHandler(self, user, channel, msg)
            for response in message_handler.response:
                self.msg(channel, response.encode())
        except Exception as e:
            self.msg(channel, "Someone f'd up. Error: " + e.message)


        # Commit any changes made by the message handler

        self.session.commit()

    def who(self, channel):
        self.sendLine('WHO %s' % channel)

    def irc_RPL_WHOREPLY(self, *nargs):
        "Receive WHO reply from server"
        print 'WHO:', nargs

    def irc_RPL_ENDOFWHO(self, *nargs):
        "Called when WHO output is complete"
        print 'WHO COMPLETE'

class SovereignFactory(protocol.ClientFactory):

    def __init__(self):
        self.bot = IAMABot()

    def buildProtocol(self, addr):
        self.bot.factory = self
        return self.bot

if __name__ == '__main__':
    sf = SovereignFactory()
    reactor.connectTCP(sf.bot.sovereign.serverhost, sf.bot.sovereign.serverport, sf)
    reactor.run()
