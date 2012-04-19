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


        user = user.split('!')[0]
        user_index = self.findUser(user)
        admin_index = self.findAdmin(user)


        # Check to see if the command the user supplied is an "order" command
        if (self.msg_split[0] in order_commands):

            channel_index = self.findChannel(channel, order_commands[self.msg_split[0]].authorized_channels)

            if (channel_index == -1):
                return

            if (self.msg_split[0].find('@update') != 0):
                self.showOrder(order_commands[self.msg_split[0]], user, channel, msg)
            else:
                self.updateOrder(order_commands[self.msg_split[0]], user, channel, msg)


        if (self.msg_split[0] == "@help"):
            self.response.append("Commands help and more info: http://kshitijparajuli.com/Sovereign/")

        if (admin_index == -1):
            return


        """
        This is _really_ ugly and is NOT the right way to do it. TODO, restructure this PoS.
        """

        if (self.msg_split[0] == "@join"):

            # Do some validation
            if (not self.verifyNumberOfParams(2)):
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
            if (not self.verifyNumberOfParams(2)):
                return
            chan_index = self.findChannel(self.msg_split[1])

            if (chan_index > -1):
                self.sovereign.ircchannels[chan_index].autojoin = False

            self.bot.part(self.msg_split[1])

        elif (self.msg_split[0] == "@adduser"):

            if (not self.verifyNumberOfParams(3)):
                return

            user_index = self.findUser(self.msg_split[1])
            if (user_index == -1):
                user_to_add = IRCUser(self.msg_split[1])
                self.sovereign.ircusers.append(user_to_add)
            else:
                user_to_add = self.sovereign.ircusers[user_index]

            if (not ("@" + self.msg_split[2]) in order_commands):
                self.response.append("Invalid orderset")
                return

            orderset = order_commands["@" + self.msg_split[2]]

            orderset.admins.append(user_to_add)

            self.response.append("Added user to orderset")

        elif (self.msg_split[0] == "@deleteuser"):

            if (not self.verifyNumberOfParams(3)):
                return

            if (not ("@" + self.msg_split[2]) in order_commands):
                self.response.append("Invalid orderset")
                return

            orderset = order_commands["@" + self.msg_split[2]]

            user_index = self.findUser(self.msg_split[1], orderset.admins)

            if (user_index == -1):
                self.response.append("User does not exist in orderset")
                return

            del orderset.admins[user_index]

            self.response.append("Deleted user from orderset")

        elif (self.msg_split[0] == "@listusers"):

            if (not self.verifyNumberOfParams(2)):
                return

            if (not ("@" + self.msg_split[1]) in order_commands):
                self.response.append("Invalid orderset")
                return

            orderset = order_commands["@" + self.msg_split[1]]

            users_list = []
            for admin in orderset.admins:
                users_list.append(admin.nick)

            self.response.append("List of users: " + (", ".join(users_list)))

        elif (self.msg_split[0] == "@addchan"):

            if (not self.verifyNumberOfParams(3)):
                return

            channel_index = self.findChannel(self.msg_split[1])

            if (channel_index == -1):
                channel_to_add = IRCChannel(self.msg_split[1])
                self.sovereign.ircchannels.append(channel_to_add)
            else:
                channel_to_add = self.sovereign.ircchannels[channel_index]

            if (not ("@" + self.msg_split[2]) in order_commands):
                self.response.append("Invalid orderset")
                return

            orderset = order_commands["@" + self.msg_split[2]]

            orderset.authorized_channels.append(channel_to_add)

            self.response.append("Added channel to orderset")

        elif (self.msg_split[0] == "@deletechan"):

            if (not self.verifyNumberOfParams(3)):
                return


            orderset = order_commands["@" + self.msg_split[2]]

            if (not ("@" + self.msg_split[2]) in order_commands):
                self.response.append("Invalid orderset")
                return

            chan_index = self.findChannel(self.msg_split[1], orderset.authorized_channels)

            if (chan_index == -1):
                self.response.append("Channel does not exist in orderset")
                return

            del orderset.authorized_channels[chan_index]

            self.response.append("Deleted channel from orderset")

        elif (self.msg_split[0] == "@listchans"):

            if (not self.verifyNumberOfParams(2)):
                return

            if (not ("@" + self.msg_split[1]) in order_commands):
                self.response.append("Invalid orderset")
                return

            orderset = order_commands["@" + self.msg_split[1]]

            chans_list = []
            for c in orderset.authorized_channels:
                chans_list.append(c.name)

            self.response.append("List of channels: " + (", ".join(chans_list)))

        elif (self.msg_split[0] == "@addadmin"):

            if (not self.verifyNumberOfParams(2)):
                return

            user_index = self.findUser(self.msg_split[1])
            if (user_index == -1):
                user_to_add = IRCUser(self.msg_split[1])
                self.sovereign.ircusers.append(user_to_add)
            else:
                user_to_add = self.sovereign.ircusers[user_index]

            user_to_add.admin = True

            self.response.append("Added user to admin")

        elif (self.msg_split[0] == "@deleteadmin"):

            if (not self.verifyNumberOfParams(2)):
                return

            user_index = self.findUser(self.msg_split[1])

            if (user_index == -1):
                self.response.append("Invalid user")
                return

            self.sovereign.ircusers[user_index].admin = False

            self.response.append("Deleted user from admin")

        elif (self.msg_split[0] == "@listadmins"):

            users_list = []
            for ircuser in self.sovereign.ircusers:
                if ircuser.admin:
                    users_list.append(ircuser.nick)

            self.response.append("List of admins: " + (", ".join(users_list)))

        elif (self.msg_split[0] == "@addorderset"):

            if (not self.verifyNumberOfParams(2)):
                return
            if (("@" + self.msg_split[1]) in order_commands):
                self.response.append("Order set already exists")
                return

            orderset_to_add = OrderSet(self.msg_split[1])
            self.sovereign.ordersets.append(orderset_to_add)

            self.response.append("Added orderset")

        elif (self.msg_split[0] == "@deleteorderset"):

            if (not self.verifyNumberOfParams(2)):
                return
            if not (("@" + self.msg_split[1]) in order_commands):
                self.response.append("Order set does not exist")
                return
            
            os_index = 0
            for order_set in self.sovereign.ordersets:
                if order_set.name == self.msg_split[1]:
                    del self.sovereign.ordersets[os_index]
                    self.response.append("Deleted orderset")
                    return
                os_index = os_index + 1
        elif (self.msg_split[0] == "@listordersets"):

            os_list = []
            for order_set in self.sovereign.ordersets:
                os_list.append(order_set.name)

            self.response.append("List of order sets: " + (", ".join(os_list)))

        elif (self.msg_split[0] == "@raw"):
            self.bot.sendLine(" ".join(self.msg_split[1:]))



    def verifyNumberOfParams(self, number):
        if (len(self.msg_split) < number):
            self.response.append("Not enough params")
            return False
        return True



    def findChannel(self, channel_name, channel_pool = None):
        channel_pool = self.sovereign.ircchannels if channel_pool == None else channel_pool
        channel_name = channel_name.lower()
        index = 0
        for irc_chan in channel_pool:
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

    def findAdmin(self, user_nick):
        user_pool = self.sovereign.ircusers
        user_nick = user_nick.lower()
        index = 0
        for irc_user in user_pool:
            if ((irc_user.nick.lower() == user_nick) & (irc_user.admin == True)):
                return index
            index = index + 1

        return -1

    def showOrder(self, order_set, user, channel, msg):
        counter = 1
        self.response = []

        for order in order_set.orders:
            message = "\002Priority %s:\002 \00302%s" % (counter, order.info)
            if (order.info.find("http:") > 0):
                urli = order.info.find('http:')
                url2end = order.info[urli:]
                message = "\002Priority %s:\002 \00304%s\017 | \037\00302%s\017 | %s" \
                 % (counter, order.info[:urli], url2end[:url2end.find(' ')], url2end[url2end.find(' '):])
            self.response.append(message)
            counter = counter + 1

        if (counter == 1):
            self.response.append("No orders found.")

    def updateOrder(self, order_set, user, channel, msg):
        if (not self.verifyNumberOfParams(2)):
            return

        self.response = []
        user = user.split('!')[0]

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
                    if (number >= 0) & (number < len(order_set.orders)):
                        del order_set.orders[number]
                        self.response.append("Order %s cleared from %s"  % ( number + 1, order_set.name))
                return

        if (number < 0):
            self.response.append("You're doing it wrong!")
            return

        if (not self.verifyNumberOfParams(3)):
            return

        info = ' '.join(self.msg_split[2:])

        if (len(order_set.orders) <= number):
            order_set.orders.append(Order(info))
        else:
            order_set.orders[number].info = info


        self.response.append("Updated orderset " + order_set.name)
