from orders import *

class SovereignMessageHandler:

    def __init__(self, sovereign, user, channel, msg):

        self.user = user
        self.channel = channel
        self.msg = msg
        self.msg_split = msg.split(' ')
        self.sovereign = sovereign
        self.response = []

        # Generate a hash linking the order fetch and receive commands to the right OrderSet
        order_commands = {}
        for order_set in sovereign.ordersets:
            order_commands["@" + order_set.name] = order_set
            order_commands["@update" + order_set.name] = order_set

        # Check to see if the command the user supplied is an "order" command
        if (self.msg_split[0] in order_commands):
            if (self.msg_split[0].find('@update') != 0):
                self.showOrder(order_commands[self.msg_split[0]], user, channel, msg)
            else:
                self.updateOrder(order_commands[self.msg_split[0]], user, channel, msg)


    def showOrder(self, order_set, user, channel, msg):
        counter = 1
        self.response = []

        for order in order_set.orders:
            message = "\002Priority %s:\002 \00304%s\017 | \037\00302%s\017 | %s" % (counter, order.territory, order.url, order.info)
            self.response.append(message)
            counter = counter + 1

        if (counter == 1):
            self.response.append("No orders found.")

    def updateOrder(self, order_set, user, channel, msg):
        self.response = []

        number = -1
        if self.msg_split[1].isdigit():
            number = int(self.msg_split[1]) - 1
        else:
            if self.msg_split[1] == "clear":
                del order_set.orders[:]
                self.response.append("Orders cleared")
                return

        if (number < 0):
            self.response.append("You're doing it wrong!")
            return

        territory = self.msg_split[2]

        if ((territory == "clear") & (len(order_set.orders) <= number)):
            del order_set.orders[number]
            self.response.append("Order cleared")
            return

        url = self.msg_split[3]
        info = self.msg_split[4]

        if (len(order_set.orders) <= number):
            order_set.orders.append(Order(territory, url, info))
        else:
            order_set.orders[number].territory = territory
            order_set.orders[number].url = url
            order_set.orders[number].info = info


        self.response.append("Updated... hopefully :3")
