from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orders import *

class IAMABot(irc.IRCClient):
	def __init__(self):
		engine = create_engine('sqlite:///bot.db')
		Session = sessionmaker(bind=engine)
		
		self.session = Session()
		self.sovereign = self.session.query(Sovereign).first()
		self.nickname = self.sovereign.nickname.encode()

	def signedOn(self):
		for chan in self.sovereign.ircchannels:
			self.join(chan.name.encode(), chan.key.encode())

	def privmsg(self, user, channel, msg):
		nick = user.split('!',1)[0]

class SovereignFactory(protocol.ClientFactory):
	def buildProtocol(self, addr):
		bot = IAMABot()
		bot.factory = self
		return bot

if __name__ == '__main__':
	sovereign = SovereignFactory()
	reactor.connectTCP("irc.rizon.net", 6667, ssovereign)
	reactor.run()
