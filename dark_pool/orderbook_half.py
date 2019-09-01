from orders import *

# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_half:

    def __init__(self, booktype):
        # booktype: bids or asks?
        self.booktype = booktype
        # a dictionary containing all traders that currently have orders in this side of the order book and the 
        # amount of orders they have
        self.traders = {}
        # list of orders received, sorted by size and then time
        self.orders = []

    # find the position to insert the order into the order_book list such that the order_book list maintains
    # it's ordering of (size,time) (where size is the original quantity of the order)
    def find_order_position(self, order):
        quantity = order.quantity
        time = order.time
        position = 0
        for i in range(0,len(self.orders)):
            if quantity > self.orders[i].quantity or (quantity == self.orders[i].quantity and time < self.orders[i].time):
                break
            else:
                position += 1
        return position

    # add the order to the order_book list
    def book_add(self, order):

        # if the trader with this tid already has an order in the order_book, then remove it
        # also set the reponse to return
        if self.traders.get(order.trader_id) != None:
            self.book_del(order.trader_id)
            response = 'Overwrite'
        else:
            response = 'Addition'
        
        # add the trader to the traders dictionary
        self.traders[order.trader_id] = 1

        # add the order to order_book list
        position = self.find_order_position(order)
        self.orders.insert(position, order)

        # return whether this was an addition or an overwrite
        return response

    # delete all orders made by the trader with the given tid
    def book_del(self, tid):
        if self.traders.get(tid) != None:
            
            # delete all orders made by the trader
            i = 0
            while i < len(self.orders):
                if self.orders[i].trader_id == tid:
                    self.orders.pop(i)
                    i -= 1
                i += 1

            # delete the trader from the traders dictinary
            del(self.traders[tid])

    # check whether a given trader has an order in this half of the order book
    def trader_has_order(self, trader_id):
        if self.traders.get(trader_id) != None:
            return True
        else:
            return False

    # return the list of orders
    def get_orders(self):
        return self.orders

    # return the dictionary of traders
    def get_traders(self):
        return self.traders

    # print the current traders
    def print_traders(self):
        for key in self.traders:
            print("%s: %d" % (key, self.traders[key]))

    # print the current orders
    def print_orders(self):
        for order in self.orders:
            print(order)