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
        lineRate = 0.5

    def signedOn(self):
        if (self.sovereign.nickservpwd != None):
            self.msg("NickServ", "IDENTIFY " + self.sovereign.nickservpwd.encode())
            self.msg("NickServ", "update")

        for chan in self.sovereign.ircchannels:
            self.join(chan.name.encode(), chan.key.encode())

    def privmsg(self, user, channel, msg):
        if (msg.find('@') == 0):
            try:
                message_handler = SovereignMessageHandler(self, user, channel, msg)
                respondto = channel if channel.find("#") == 0 else user.split("!")[0]
                for response in message_handler.response:
                    self.msg(respondto, response.encode())
                # Commit any changes made by the message handler
                self.session.commit()
            except Exception as e:
                self.msg(channel, "Something went wrong. Error: " + e.message)




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
