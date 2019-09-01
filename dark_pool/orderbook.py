from orders import *
from orderbook_half import *

# Orderbook for a single instrument: list of bids and list of asks
class Orderbook:

    def __init__(self):
        self.buy_side = Orderbook_half('Buy')
        self.sell_side = Orderbook_half('Sell')
        self.tape = []
        self.order_id = 0  #unique ID code for each quote accepted onto the book
        self.traders = {}

    # add an order to the order book
    def add_order(self, order, verbose):

        # give the order a unique ID
        order.id = self.order_id
        self.order_id = order.id + 1

        # add the order to the correct side of the order book
        if order.otype == 'Buy':
            response=self.buy_side.book_add(order)
            # If the trader already has an order on the sell side then delete it
            if self.sell_side.trader_has_order(order.trader_id):
                self.sell_side.book_del(order.trader_id)
                response='Overwrite'

        elif order.otype == 'Sell':
            response=self.sell_side.book_add(order)
            # If the trader already has an order on the buy side then delete it
            if self.buy_side.trader_has_order(order.trader_id):
                self.buy_side.book_del(order.trader_id)
                response = 'Overwrite'

        # return the order ID and whether or not the order was an addition or an overwrite
        return [order.id, response]

    # check whether a given trader currently has an order in the order book
    def trader_has_order(self, trader_id):
        if self.buy_side.trader_has_order(trader_id) or self.sell_side.trader_has_order(trader_id):
            return True
        else:
            return False

    # delete all orders made by a trader
    def book_del(self, trader_id):
        self.buy_side.book_del(trader_id)
        self.sell_side.book_del(trader_id)

    # delete an order from the order book
    def del_order(self, time, order, verbose):
        # delete a trader's order from the exchange, update all internal records
        if order.otype == 'Buy':
            self.buy_side.book_del(order.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'order': order }
            self.tape.append(cancel_record)

        elif order.otype == 'Sell':
            self.sell_side.book_del(order.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'order': order }
            self.tape.append(cancel_record)
        else:
            # neither bid nor ask?
            sys.exit('bad order type in del_quote()')

    # Check that two orders match in terms of their price
    def check_price_match(self, buy_order, sell_order, price):

        if buy_order.limit_price == None and sell_order.limit_price == None:
            return True

        elif buy_order.limit_price != None and sell_order.limit_price == None:
            if buy_order.limit_price >= price:
                return True

        elif buy_order.limit_price == None and sell_order.limit_price != None:
            if sell_order.limit_price <= price:
                return True

        elif buy_order.limit_price != None and sell_order.limit_price != None:
            if buy_order.limit_price >= price and sell_order.limit_price <= price:
                return True

        return False

    # Check that two orders match in terms of their size
    def check_size_match(self, buy_order, sell_order):

        if buy_order.MES == None and sell_order.MES == None:
            return True

        elif buy_order.MES != None and sell_order.MES == None:
            if sell_order.quantity_remaining >= buy_order.MES:
                return True

        elif buy_order.MES == None and sell_order.MES != None:
            if buy_order.quantity_remaining >= sell_order.MES:
                return True

        elif buy_order.MES != None and sell_order.MES != None:
            if buy_order.quantity_remaining >= sell_order.MES and \
            sell_order.quantity_remaining >= buy_order.MES:
                return True

        return False

    # check that both the order size and the price match between the two given orders
    def check_match(self, buy_order, sell_order, price):
        return self.check_price_match(buy_order, sell_order, price) and \
        self.check_size_match(buy_order, sell_order)



    # Find a match between a buy order and a sell order
    def find_matching_orders(self, price):

        # get the list of buy orders and sell orders
        buy_orders = self.buy_side.get_orders()
        sell_orders = self.sell_side.get_orders()

        # matching is buy-side friendly, so start with buys first
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                # check that the two orders match with eachother
                if self.check_match(buy_order, sell_order, price):

                    # return a dictionary containing the match info
                    # Note. Here we are returning references to the orders, so changing the returned orders will
                    # change the orders in the order_book
                    return {
                        "buy_order": buy_order, 
                        "sell_order": sell_order,
                        "price": price
                    }

        # if no match can be found, return None
        return None

    # perform the trade specified in the trade_info dictionary
    def execute_trade(self, time, trade_info):

        # calculate the trade size
        if trade_info["buy_order"].quantity_remaining >= trade_info["sell_order"].quantity_remaining:
            trade_size = trade_info["sell_order"].quantity_remaining
        else:
            trade_size = trade_info["buy_order"].quantity_remaining

        # remove the orders from the order_book
        self.buy_side.book_del(trade_info["buy_order"].trader_id)
        self.sell_side.book_del(trade_info["sell_order"].trader_id)

        # subtract the trade quantity from each orders' quantity remaining
        trade_info["buy_order"].quantity_remaining -= trade_size
        trade_info["sell_order"].quantity_remaining -= trade_size

        # re-add the the order with the leftover quantity
        if trade_info["buy_order"].quantity_remaining > 0:
            # update the MES if necessary
            if trade_info["buy_order"].MES > trade_info["buy_order"].quantity_remaining:
                trade_info["buy_order"].MES = trade_info["buy_order"].quantity_remaining
            # add the order to the order_book list
            self.buy_side.book_add(trade_info["buy_order"])

        # re-add the order with the leftover quantity
        if trade_info["sell_order"].quantity_remaining > 0:
            # update the MES if necessary
            if trade_info["sell_order"].MES > trade_info["sell_order"].quantity_remaining:
                trade_info["sell_order"].MES = trade_info["sell_order"].quantity_remaining
            # add the order to the order_book list
            self.sell_side.book_add(trade_info["sell_order"])

        # create a record of the transaction 
        # BDS specifies whether the orders orginated from the block discovery service
        transaction_record = {  
            'type': 'Trade',
            'time': time,
            'price': trade_info["price"],
            'quantity': trade_size,
            'buyer': trade_info["buy_order"].trader_id,
            'seller': trade_info["sell_order"].trader_id,
            'BDS': trade_info["buy_order"].BDS and trade_info["sell_order"].BDS
        }

        # add the record to the tape
        self.tape.append(transaction_record)

        # return the transaction
        return transaction_record


    # trades occur at the given time at the given price
    # keep making trades out of matched orders until no more matches can be found
    def execute_trades(self, time, price):

        # a list of all the trades made
        trades = []

        # find a match between a buy order a sell order
        match_info = self.find_matching_orders(price)

        # keep on going until no more matches can be found
        while match_info != None:

            # execute the trade with the matched orders
            trade = self.execute_trade(time, match_info)

            # add the trade information to the list of trades
            trades.append(trade)

            # find another match
            match_info = self.find_matching_orders(price)
            
        # return the list of trades
        return trades


    # write the tape to an output file
    def tape_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        # write the title for each column
        dumpfile.write('time, buyer, seller, quantity, price, BDS\n')
        # write the information for each trade
        for tapeitem in self.tape:
            if tapeitem['type'] == 'Trade' :
                if tapeitem['BDS']:
                    BDS = "Yes"
                else:
                    BDS = ""
                dumpfile.write('%.2f, %s, %s, %s, %s, %s\n' % (tapeitem['time'], tapeitem['buyer'], tapeitem['seller'], tapeitem['quantity'], tapeitem['price'], BDS))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []

    # print the current orders in the orders dictionary
    def print_traders(self):
        print("Buy orders:")
        self.buy_side.print_traders()
        print("Sell orders:")
        self.sell_side.print_traders()

    # print the current orders in the order_book list
    def print_order_book(self):
        print("Order Book:")
        print("Buy side:")
        self.buy_side.print_orders()
        print("Sell side:")
        self.sell_side.print_orders()
        print("")

    # print the tape
    def print_tape(self):
        print("Tape:")
        for trade in self.tape:
            print(trade)
        print("")
