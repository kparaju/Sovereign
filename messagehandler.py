from orders import *

class SovereignMessageHandler:

    def __init__(self, bot, user, channel, msg):

        self.user = user
        self.channel = channel
        self.msg = msg
        self.msg_split = msg.split(' ')
        self.sovereign = bot.sovereign
        self.bot = bot
        self.response = []

        # Generate a hash linking the order fetch and receive commands to the right OrderSet
        order_commands = {}
        for order_set in self.sovereign.ordersets:
            order_commands["@" + order_set.name] = order_set
            order_commands["@update" + order_set.name] = order_set

        # Check to see if the command the user supplied is an "order" command
        if (self.msg_split[0] in order_commands):
            if (self.msg_split[0].find('@update') != 0):
                self.showOrder(order_commands[self.msg_split[0]], user, channel, msg)
            else:
                self.updateOrder(order_commands[self.msg_split[0]], user, channel, msg)

        elif (self.msg_split[0] == "@join"):

            # Do some validation
            if (len(self.msg_split) < 2):
                self.response.append("Not enough params")
                return

            channel_to_join = self.msg_split[1]
            channel_password = self.msg_split[2] if (len(self.msg_split) > 2) else ''

            # Search for the channel in the database
            chan_index = self.findChannel(channel_to_join)
            if (chan_index == -1):
                # Does not exist, create an entry and append it
                chan = IRCChannel(channel_to_join, channel_password)
                self.sovereign.ircchannels.append(chan)
            else:
                self.sovereign.ircchannels[chan_index].key = channel_password
                self.sovereign.ircchannels[chan_index].autojoin = True

            self.bot.join(channel_to_join, channel_password)

        elif (self.msg_split[0] == "@part"):
            if (len(self.msg_split) < 2):
                self.response.append("Not enough params")
                return

            chan_index = self.findChannel(self.msg_split[1])

            if (chan_index > -1):
                self.sovereign.ircchannels[chan_index].autojoin = False

            self.bot.part(self.msg_split[1])



    def findChannel(self, channel_name, channel_pool = None):
        channel_pool = self.sovereign.ircchannels if channel_pool == None else channel_pool
        channel_name = channel_name.lower()
        index = 0
        for irc_chan in self.sovereign.ircchannels:
            if (irc_chan.name.lower() == channel_name):
                return index
            index = index + 1

        return -1

    def findUser(self, user_nick, user_pool = None):
        user_pool = self.sovereign.ircusers if user_pool == None else user_pool
        user_nick = user_nick.lower()
        index = 0
        for irc_user in user_pool:
            if (irc_user.nick.lower() == user_nick):
                return index
            index = index + 1

        return -1

    def showOrder(self, order_set, user, channel, msg):
        counter = 1
        self.response = []

        for order in order_set.orders:
            message = "\002Priority %s:\002 \00304%s\017 | \037\00302%s\017 | %s" \
                        % (counter, order.territory, order.url, order.info)
            self.response.append(message)
            counter = counter + 1

        if (counter == 1):
            self.response.append("No orders found.")

    def updateOrder(self, order_set, user, channel, msg):
        self.response = []

        user_index = self.findUser(user, order_set.admins)

        if (user_index == -1):
            self.response.append("Not authorized")
            return

        number = -1
        if self.msg_split[1].isdigit():
            number = int(self.msg_split[1]) - 1
        else:
            if self.msg_split[1] == "clear":
                if (len(self.msg_split) < 3):
                    del order_set.orders[:]
                    self.response.append("Orders cleared")
                else:
                    number = int(self.msg_split[2]) - 1
                    if (number >= 0) & (number < len(self.msg_split)):
                        del order_set.orders[number]
                        self.response.append("Order cleared")
                return

        if (number < 0):
            self.response.append("You're doing it wrong!")
            return

        territory = self.msg_split[2]
        url = self.msg_split[3]
        info = self.msg_split[4]

        if (len(order_set.orders) <= number):
            order_set.orders.append(Order(territory, url, info))
        else:
            order_set.orders[number].territory = territory
            order_set.orders[number].url = url
            order_set.orders[number].info = info


        self.response.append("Updated... hopefully.")
