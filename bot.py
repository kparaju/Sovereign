from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

import time, sys

from sqlalchemy import create_engine

class IAMABot(irc.IRCClient):
	
	sovereign = Sovereign("Sovereign_Beta")

	engine = create_engine('sqlite:///:memory:', echo=True)

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		
	def privmsg(self, user, channel, msg):
		nick = user.split('!',1)[0]

		if (msg == "@hello"):


	
