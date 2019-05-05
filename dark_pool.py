import sys
import math
import random
import copy


bse_sys_minprice = 1  # minimum price in the system, in cents/pennies
bse_sys_maxprice = 1000  # maximum price in the system, in cents/pennies
ticksize = 1  # minimum change in price, in cents/pennies


#######################-Customer_Order Class-########################


# a customer order which is given to a trader to complete
class Customer_Order:

    def __init__(self, time, tid, otype, price, qty):
        self.time = time      # the time the customer order was issued
        self.trader_id = tid        # the trader i.d. that this order is for
        self.otype = otype    # the order type of the customer order i.e. buy/sell
        self.price = price    # the limit price of the customer order
        self.quantity = qty        # the quantity to buy/sell

    def __str__(self):
        return 'Customer Order [T=%5.2f %s %s P=%s Q=%s]' % (self.time, self.trader_id, self.otype, self.price, 
            self.quantity)


#######################-Order Class-################################


# An order created by a trader for the exchange.
class Order:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES):
        self.id = -1                    # order i.d. (unique to each order on the Exchange)
        self.time = time                # timestamp
        self.trader_id = trader_id      # trader i.d.
        self.otype = otype              # order type
        self.quantity = quantity        # the original quantity of the order
        self.limit_price = limit_price  # limit price, None means no limit price
        self.MES = MES                  # minimum execution size, None means no MES
        self.BDS = False
        self.BDS_match_id = None
        self.quantity_remaining = quantity # the remaining on the order

    def __str__(self):
        return 'Order: [ID=%d T=%5.2f %s %s Q=%s QR=%s P=%s MES=%s]' % (self.id, self.time, self.trader_id, self.otype, 
            self.quantity, self.quantity_remaining, self.limit_price, self.MES)


######################-Block_Indication Class-#######################################


# A block indication created by a trader for the exchange
class Block_Indication:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES

    def __str__(self):
        return 'BI: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s]' % (self.id, self.time, self.trader_id, 
            self.otype, self.quantity, self.limit_price, self.MES)


#########################-Order Submission Request Class-############################

# An Order Submission Request (OSR) sent to a trader when their block indication is matched
class Order_Submission_Request:

    def __init__(self, OSR_id, time, trader_id, otype, quantity, limit_price, MES, match_id, reputational_score):
        self.id = OSR_id
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES
        self.match_id = match_id
        self.reputational_score = reputational_score

    def __str__(self):
        return 'OSR: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s MID=%d CRP=%s]' % (self.id, self.time, self.trader_id, 
            self.otype, self.quantity, self.limit_price, self.MES, self.match_id, self.reputational_score)


#########################-Qualifying_Block_Order Class-###############################

# A Qualifying Block Order (QBO) created by a trader for the exchange
class Qualifying_Block_Order:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES, match_id):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES
        self.match_id = match_id

    def __str__(self):
        return 'QBO: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s MID=%d]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.limit_price, self.MES, self.match_id)


########################-Orderbook_half Class-#################


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


###################-Orderbook Class-#############################


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


#####################-Block_Indication_Book Class-########################


# Block Indication Book class for a single instrument. The class holds and performs operations with 
# received block indications
class Block_Indication_Book:

    # constructer function for the Block_Indication_Book class
    def __init__(self):
        # The buy side contains all of the block indications to buy
        self.buy_side = Orderbook_half('Buy')
        # The sell side contains all of the block indications to sell
        self.sell_side = Orderbook_half('Sell')
        # The Minimum Indication Value (MIV) is the quantity that a block indication must be greater
        # than in order to be accepted
        self.MIV = 500
        # ID to be given to next Block Indication
        self.BI_id = 0
        # ID to be given to next Qualifying Block Order received
        self.QBO_id = 0
        # ID to be given to the next OSR created
        self.OSR_id = 0
        # The composite_reputational_scores dictionary contains the composite reputational score for each trader. 
        self.composite_reputational_scores = {}
        # The event_reputation_scores dictionary contains the last 50 event reputational scores for each trader.
        self.event_reputational_scores = {}
        # the initial composite reputational score given to each trader
        self.initial_reputational_score = 100
        # the Reputational Score Threshold (RST). All traders with a composite reputational score below this threshold
        # are no longer able to use the block discovery service
        self.RST = 75
        # A dictionary to hold matched BIs and the corresponding QBOs
        self.matches = {}
        # ID to be given to the matching of two block indications
        self.match_id = 0
        # The tape contains the history of block indications sent to the exchange
        self.tape = []
        # The entire history of each trader's score
        self.composite_reputational_scores_history = {}

    
    # Add a block indication to the exchange
    def add_block_indication(self, BI, verbose):

        # if a new trader, then give it an initial reputational score
        if self.composite_reputational_scores.get(BI.trader_id) == None:
            self.composite_reputational_scores[BI.trader_id] = self.initial_reputational_score
            self.event_reputational_scores[BI.trader_id] = [self.initial_reputational_score for i in range(0,50)]
            self.composite_reputational_scores_history[BI.trader_id] = [(0, self.initial_reputational_score)]

        # the quantity of the order must be greater than the MIV
        # the trader must also have a composite reputational score lower than the RST
        if BI.quantity >= self.MIV and self.composite_reputational_scores.get(BI.trader_id) >= self.RST:

            # give an ID to the block indication
            BI.id = self.BI_id
            self.BI_id = BI.id + 1

            # add the block indication to the correct order book
            if BI.otype == 'Buy':
                response=self.buy_side.book_add(BI)
                # If the trader already has a block indication on the sell side, then delete it
                if self.sell_side.trader_has_order(BI.trader_id):
                    self.sell_side.book_del(BI.trader_id)
                    response = 'Overwrite'

            elif BI.otype == 'Sell':
                response=self.sell_side.book_add(BI)
                # If the trader already has a block indication on the buy side, then delete it
                if self.buy_side.trader_has_order(BI.trader_id):
                    self.buy_side.book_del(BI.trader_id)
                    response = 'Overwrite'

            # return the block indication id and the response
            return [BI.id, response]

        # if the block indication was rejected then return the message
        return [-1, "Block Indication Rejected"]

    # check whether a given trader currently has a block indication
    def trader_has_block_indication(self, trader_id):
        if self.buy_side.trader_has_order(trader_id) or self.sell_side.trader_has_order(trader_id):
            return True
        else:
            return False

    # detete all block indications made by a given trader
    def book_del(self, trader_id):
        self.buy_side.book_del(trader_id)
        self.sell_side.book_del(trader_id)

    # delete block indication
    def del_block_indication(self, time, BI, verbose):
        # delete a trader's order from the exchange, update all internal records
        if BI.otype == 'Buy':
            self.buy_side.book_del(BI.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'BI': BI }
            self.tape.append(cancel_record)

        elif BI.otype == 'Sell':
            self.sell_side.book_del(BI.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'BI': BI }
            self.tape.append(cancel_record)
        else:
            sys.exit('bad order type in del_block_indication()')

    # check that two block indications match in terms of their price
    def check_price_match(self, buy_BI, sell_BI, price):

        if buy_BI.limit_price == None and sell_BI.limit_price == None:
            return True

        elif buy_BI.limit_price != None and sell_BI.limit_price == None:
            if buy_BI.limit_price >= price:
                return True

        elif buy_BI.limit_price == None and sell_BI.limit_price != None:
            if sell_BI.limit_price <= price:
                return True

        elif buy_BI.limit_price != None and sell_BI.limit_price != None:
            if buy_BI.limit_price >= price and sell_BI.limit_price <= price:
                return True

        return False

    # check that two block indications match in terms of their size
    def check_size_match(self, buy_BI, sell_BI):

        if buy_BI.MES == None and sell_BI.MES == None:
            return True

        elif buy_BI.MES != None and sell_BI.MES == None:
            if sell_BI.quantity >= buy_BI.MES:
                return True

        elif buy_BI.MES == None and sell_BI.MES != None:
            if buy_BI.quantity >= sell_BI.MES:
                return True

        elif buy_BI.MES != None and sell_BI.MES != None:
            if buy_BI.quantity >= sell_BI.MES and sell_BI.quantity >= buy_BI.MES:
                return True

        return False

    # check that two block indications match
    def check_match(self, buy_BI, sell_BI, price):
        # check that both the order size and the price match
        return self.check_price_match(buy_BI, sell_BI, price) and self.check_size_match(buy_BI, sell_BI)

    # attempt to find two matching block indications
    def find_matching_block_indications(self, price):
        
        # get the buy block indications list and sell block indications list
        buy_BIs = self.buy_side.get_orders()
        sell_BIs = self.sell_side.get_orders()

        # starting with the buy side first
        for buy_BI in buy_BIs:
            for sell_BI in sell_BIs:
                # check if the two block indications match
                if self.check_match(buy_BI, sell_BI, price):
                    
                    # Add the matched BIs to the matches dictionary
                    self.matches[self.match_id] = {
                        "buy_BI": buy_BI, 
                        "sell_BI": sell_BI,
                        "buy_QBO": None,
                        "sell_QBO": None
                    }

                    # get the current match id
                    match_id = self.match_id

                    # increment the book's match_id counter
                    self.match_id += 1

                    # delete these block indications from the block indication book
                    self.del_block_indication(0, buy_BI, False)
                    self.del_block_indication(0, sell_BI, False)

                    # return the match id
                    return match_id

        # if no match was found then return None
        return None

    # attempt to find two matching block indications
    def find_all_matching_block_indications(self, price):

        match_id = self.find_matching_block_indications(price)

        while match_id != None:
            match_id = self.find_matching_block_indications(price)

    # return a match given the ID
    def get_block_indication_match(self, match_id):
        return self.matches.get(match_id)

    # create the order submissions requests given a match between two block indications
    def create_order_submission_requests(self, match_id):
        # Get the block indications.
        buy_BI = self.matches[match_id]["buy_BI"]
        sell_BI = self.matches[match_id]["sell_BI"]

        # Get the composite reputational scores.
        buy_CRP = self.composite_reputational_scores[buy_BI.trader_id]
        sell_CRP = self.composite_reputational_scores[sell_BI.trader_id]
        
        # create the buy side OSR
        buy_OSR = Order_Submission_Request(self.OSR_id,
                                                buy_BI.time,
                                                buy_BI.trader_id,
                                                buy_BI.otype,
                                                buy_BI.quantity,
                                                buy_BI.limit_price,
                                                buy_BI.MES,
                                                match_id,
                                                buy_CRP)

        # increment the OSR id counter
        self.OSR_id += 1

        # create the sell side OSR
        sell_OSR = Order_Submission_Request(self.OSR_id,
                                                 sell_BI.time,
                                                 sell_BI.trader_id,
                                                 sell_BI.otype,
                                                 sell_BI.quantity,
                                                 sell_BI.limit_price,
                                                 sell_BI.MES,
                                                 match_id,
                                                 sell_CRP)

        # increment the OSR id counter
        self.OSR_id += 1

        # return both OSRs in a dicitionary
        return {"buy_OSR": buy_OSR, "sell_OSR": sell_OSR}

    # add a Qualifying Block Order (QBO). QBOs are added to the appropriate entry in the matches dictionary.
    def add_qualifying_block_order(self, QBO, verbose):

        # give each qualifying block order its own unique id
        QBO.id = self.QBO_id
        self.QBO_id += 1

        # get the match id for the orginally matched block indications
        match_id = QBO.match_id

        # add the qualifying block order to the match in the matches dictionary
        if self.matches.get(match_id) != None:
            if QBO.otype == 'Buy':
                self.matches[match_id]["buy_QBO"] = QBO
            elif QBO.otype == "Sell":
                self.matches[match_id]["sell_QBO"] = QBO
        else:
            return "Incorrect match id."
        
        # check if both QBOs have been received
        if self.matches[match_id]["buy_QBO"] and self.matches[match_id]["sell_QBO"]:
            return "Both QBOs have been received."
        else:
            return "First QBO received."

    # Compare a QBO with a BI to see whether or not its price is marketable
    def marketable_price(self, BI, QBO):

        if BI.limit_price == None and QBO.limit_price == None:
            return True

        elif BI.limit_price != None and QBO.limit_price == None:
            return True

        elif BI.limit_price != None and QBO.limit_price != None:
            if BI.otype == 'Buy':
                if QBO.limit_price >= BI.limit_price:
                    return True
            if BI.otype == 'Sell':
                if QBO.limit_price <= BI.limit_price:
                    return True

        return False

    # Compare a QBO with a BI to see whether or not its size is marketable
    def marketable_size(self, BI, QBO):

        if BI.MES == None and QBO.MES == None:
            return True

        elif BI.MES != None and QBO.MES == None:
            return True

        elif BI.MES != None and QBO.MES != None:
            if QBO.MES <= BI.MES:
                return True

        return False


    # compare a QBO with its BI to see whether it is marketable
    def marketable(self, BI, QBO):
        return self.marketable_price(BI, QBO) and self.marketable_size(BI, QBO)

    # calculate the reputational score of a trader for a single event. If the QBO is not marketable, then the
    # event reputation score is 0. If the QBO is marketable then score will be between 50 and 100
    def calculate_event_reputational_score(self, BI, QBO):

        # Check that the QBO is marketable
        if self.marketable(BI, QBO):

            event_reputational_score = 100

            # calculate the difference between the QBO quantity and the BI quantity as a decimal
            quantity_dec_diff = (BI.quantity - QBO.quantity) / BI.quantity

            # if the QBO quantity is less than the BI quantity then decrease score
            # The function used here is y = 77.1(e^x - 1)
            if quantity_dec_diff > 0:
                event_reputational_score -= round(77.1 * (math.exp(quantity_dec_diff) - 1))

            # Make sure that the score is not less than 50
            if event_reputational_score < 50: 
                event_reputational_score = 50

        # If the QBO is not marketable then the score is 0
        else:
            event_reputational_score = 0

        # Add this event reputational score to the dictionary containing the last 50 event reputational scores
        # for each trader
        self.event_reputational_scores[BI.trader_id].insert(0,event_reputational_score)
        # make sure that the list only contains the last 50 event reputational scores
        self.event_reputational_scores[BI.trader_id] = self.event_reputational_scores[BI.trader_id][:50]

        # return the score
        return event_reputational_score

    # Calculate a trader's composite reputational score.
    # The most recent event reputational score has a weighting of 50, 
    # the next most recent 49, and so on
    def calculate_composite_reputational_score(self, tid):

        # The current weighting
        weighting = 50
        # The sum of the event reputational scores multiplied by their weighting
        total = 0.0

        for i in range(0, 50):
            total += weighting * self.event_reputational_scores[tid][i]
            weighting -= 1

        # Calculate the composite reputational score rounded to the nearest integer
        composite_reputational_score = int(round(total / 1275))

        # return the composite reputational score
        return composite_reputational_score
        

    # update both traders' reputation score given this matching event
    def update_composite_reputational_scores(self, time, match_id):

        # get the BIs and the QBOs from the matches dictionary item
        buy_BI = self.matches[match_id]["buy_BI"]
        sell_BI = self.matches[match_id]["sell_BI"]
        buy_QBO = self.matches[match_id]["buy_QBO"]
        sell_QBO = self.matches[match_id]["sell_QBO"]

        # calculate the event reputation scores (they will be added to list of event reputational scores for each trader)
        self.calculate_event_reputational_score(buy_BI, buy_QBO)
        self.calculate_event_reputational_score(sell_BI, sell_QBO)

        # update the traders' reputational score
        buyer_composite_reputational_score = self.calculate_composite_reputational_score(buy_BI.trader_id)
        seller_composite_reputational_score = self.calculate_composite_reputational_score(sell_BI.trader_id)
        self.composite_reputational_scores[buy_BI.trader_id] = buyer_composite_reputational_score
        self.composite_reputational_scores[sell_BI.trader_id] = seller_composite_reputational_score

        # add the scores to the trader history
        self.composite_reputational_scores_history[buy_BI.trader_id].append((time, buyer_composite_reputational_score))
        self.composite_reputational_scores_history[sell_BI.trader_id].append((time, seller_composite_reputational_score))

    # delete a match from the matches dictonary given the match ID
    def delete_match(self, match_id):
        del(self.matches[match_id])

    # write the composite reputational scores history to an output file
    def composite_reputational_scores_history_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)

        # find the length of the longest list of scores
        highest_length = 0
        for trader in self.composite_reputational_scores_history.keys():
            this_length = len(self.composite_reputational_scores_history[trader])
            if this_length > highest_length:
                highest_length = this_length

        # write the column names
        for trader in sorted(self.composite_reputational_scores_history.keys()):
            dumpfile.write('%s: %d scores,,' % (trader, len(self.composite_reputational_scores_history[trader])))
        dumpfile.write('\n')
        for i in range(0, len(self.composite_reputational_scores_history)):
            dumpfile.write('time,score,')
        dumpfile.write('\n')

        # write each row containing a time and score for each trader
        for i in range(0, highest_length):
            for trader in sorted(self.composite_reputational_scores_history.keys()):
                if i < len(self.composite_reputational_scores_history[trader]):
                    (time, score) = self.composite_reputational_scores_history[trader][i]
                    dumpfile.write('%.2f, %d,' % (time, score))
                else:
                    dumpfile.write(',,')
            dumpfile.write('\n')

        # clost the file
        dumpfile.close()

        if tmode == 'wipe':
            self.tape = []

    # write the composite reputational scores history to an output file
    def event_reputational_scores_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)

        # write the column names
        for trader in sorted(self.event_reputational_scores.keys()):
            dumpfile.write('%s,,' % trader)
        dumpfile.write('\n')
        for i in range(0, len(self.event_reputational_scores)):
            dumpfile.write('time,score,')
        dumpfile.write('\n')

        # write each row containing a time and score for each trader
        for i in range(0, 50):
            for trader in sorted(self.event_reputational_scores.keys()): 
                score = self.event_reputational_scores[trader][i]
                dumpfile.write('%d,' % score)
            dumpfile.write('\n')

        # clost the file
        dumpfile.close()

        if tmode == 'wipe':
            self.tape = []

    # print the composite reputational score of all known traders
    def print_composite_reputational_scores(self):
        print("Reputational scores:")
        for key in self.composite_reputational_scores:
            print("%s : %d" % (key, self.composite_reputational_scores[key]))
        print("")

    # print the event reputational scores of all known traders
    def print_event_reputational_scores(self):
        print("Event reputational scores:")
        for key in self.event_reputational_scores:
            print "%s:" % key,
            for score in self.event_reputational_scores[key]:
                print "%d" % score,
            print("")

    # print all traders that currently have block indications
    def print_traders(self):
        print("Buy orders:")
        self.buy_side.print_traders()
        print("Sell orders:")
        self.sell_side.print_traders()

    # print the current block indications
    def print_block_indications(self):
        print("Block Indications:")
        print("Buy side:")
        self.buy_side.print_orders()
        print("Sell side:")
        self.sell_side.print_orders()
        print("")

    # print the current matches
    def print_matches(self):
        print("Matches:")
        for key in self.matches.keys():
            print("Match id: %d" % key)
            print(self.matches[key]["buy_BI"])
            print(self.matches[key]["sell_BI"])
            if self.matches[key]["buy_QBO"]:
                print(self.matches[key]["buy_QBO"])
            if self.matches[key]["sell_QBO"]:
                print(self.matches[key]["sell_QBO"])
        print("")


####################-Exchange Class-################################


# Exchange class. This class is used to bring together the Orderbook class and the Block_Indication_Book class.
class Exchange:

    # constructor method
    def __init__(self):
        # order_book will hold all of the orders made by traders
        self.order_book = Orderbook()
        # block_indication_book will hold all of the block indications made by traders 
        self.block_indication_book = Block_Indication_Book()

    # add an order to the exchange
    def add_order(self, order, verbose):
        # Make sure that what is being added is actually an order
        if(isinstance(order, Order)):
            # Add the order to the exchange
            [order_id, response] = self.order_book.add_order(order, verbose)
            # If the trader already has a block indication on the exchange, then delete it
            if self.block_indication_book.trader_has_block_indication(order.trader_id):
                self.block_indication_book.book_del(order.trader_id)
                response = 'Overwrite'
            # Return the order id and the response
            return [order_id, response]
        else:
            return [-1, "Not an Order."]
    
    # add a block indication to the exchange
    def add_block_indication(self, BI, verbose):
        # Make sure that what is being added is actually a block indication
        if(isinstance(BI, Block_Indication)):
            # Add the block indication to the exchange
            [BI_id, response] = self.block_indication_book.add_block_indication(BI, verbose)
            # If the trader already has an order in the order book, then delete it
            if response != "Block Indication Rejected" and self.order_book.trader_has_order(BI.trader_id):
                self.order_book.book_del(BI.trader_id)
                response = 'Overwrite'
            # Return the block indication ID and the response
            return [BI_id, response]
        else:
            return [-1, "Not a Block Indication."]

    # add a qualifying block order to the exchange
    def add_qualifying_block_order(self, QBO, verbose):
        if(isinstance(QBO, Qualifying_Block_Order)):
            return self.block_indication_book.add_qualifying_block_order(QBO, verbose)
        else:
            return "Not a Qualifying Block Order."

    # convert Qualifying Block Orders into firm orders
    def add_firm_orders_to_order_book(self, match_id):

        # get the QBOs from the match
        full_match = self.block_indication_book.get_block_indication_match(match_id)
        buy_QBO = full_match["buy_QBO"]
        sell_QBO = full_match["sell_QBO"]

        # Here is where the problem lies when I was trying to create the reputational scoring graph
        # The QBOs are converted into orders and added to the order book
        # If these orders cannot match on the order book then the trade doesn't go through
        # However a new composite reputational score has already been calculated.
        # So the event reputational score is updated but a trade doesn't go through, which was confusing me.

        # create orders out of the QBOs
        buy_order = Order(buy_QBO.time,
                               buy_QBO.trader_id,
                               buy_QBO.otype,
                               buy_QBO.quantity,
                               buy_QBO.limit_price,
                               buy_QBO.MES)
        sell_order = Order(sell_QBO.time,
                                sell_QBO.trader_id,
                                sell_QBO.otype,
                                sell_QBO.quantity,
                                sell_QBO.limit_price,
                                sell_QBO.MES)

        # add the orders to the order book
        buy_order.BDS = True
        buy_order.BDS_match_id = match_id
        sell_order.BDS = True
        sell_order.BDS_match_id = match_id
        self.add_order(buy_order, False)
        self.add_order(sell_order, False)


    # match block indications that are lying in the exchange and then convert those block indications 
    # into firm orders
    def match_block_indications_and_get_firm_orders(self, time, traders, price):
        
        # find all block indication matches
        self.block_indication_book.find_all_matching_block_indications(price)

        # go through all matches
        for match_id in self.block_indication_book.matches.keys():

            # get the block indications that were matched
            full_match = self.block_indication_book.get_block_indication_match(match_id)
            buy_BI = full_match["buy_BI"]
            sell_BI = full_match["sell_BI"]

            # send an OSR to each traders and get back a QBO
            OSRs = self.block_indication_book.create_order_submission_requests(match_id)
            buy_QBO = traders[buy_BI.trader_id].get_qualifying_block_order(time, OSRs["buy_OSR"])
            sell_QBO = traders[sell_BI.trader_id].get_qualifying_block_order(time, OSRs["sell_OSR"])

            # add the QBOs to the exchange
            self.block_indication_book.add_qualifying_block_order(buy_QBO, False)
            self.block_indication_book.add_qualifying_block_order(sell_QBO, False)

            # update the reputational scores of the traders in the match
            self.block_indication_book.update_composite_reputational_scores(time, match_id)

            # add the firm orders to the order book.
            self.add_firm_orders_to_order_book(match_id)
            
            # delete the block indication match from the matches dictionary
            self.block_indication_book.delete_match(match_id)


    # write the order_book's tape to the output file
    def tape_dump(self, fname, fmode, tmode):
        self.order_book.tape_dump(fname, fmode, tmode)

    # write the order_book's tape to the output file
    def composite_reputational_scores_history_dump(self, fname, fmode, tmode):
        self.block_indication_book.composite_reputational_scores_history_dump(fname, fmode, tmode)

    # write the order_book's tape to the output file
    def event_reputational_scores_dump(self, fname, fmode, tmode):
        self.block_indication_book.event_reputational_scores_dump(fname, fmode, tmode)

    # delete an order from the exchange
    def del_order(self, time, order, verbose):
        return self.order_book.del_order(time, order, verbose)

    def del_block_indication(self, time, order, verbose):
        return self.block_indication_book.del_block_indication(time, order, verbose)

    def execute_trades(self, time, price):
        return self.order_book.execute_trades(time, price)

    # print the current orders in the orders dictionary
    def print_traders(self):
        self.order_book.print_traders()

    # print the current orders in the order_book list
    def print_order_book(self):
        self.order_book.print_order_book()

    def print_block_indication_traders(self):
        self.block_indication_book.print_block_indication_traders()

    def print_block_indications(self):
        self.block_indication_book.print_block_indications()

    def print_composite_reputational_scores(self):
        self.block_indication_book.print_composite_reputational_scores()

    def print_event_reputational_scores(self):
        self.block_indication_book.print_event_reputational_scores()

    def print_qualifying_block_orders(self):
        self.block_indication_book.print_qualifying_block_orders()

    def print_matches(self):
        self.block_indication_book.print_matches()


##################--Traders below here--#############


# Trader superclass
# all Traders have a trader id, bank balance, blotter, and list of orders to execute
class Trader:

    def __init__(self, ttype, tid, balance, time):
        self.ttype = ttype             # what type / strategy this trader is
        self.trader_id = tid           # trader unique ID code
        self.balance = balance         # money in the bank
        self.blotter = []              # record of trades executed
        self.customer_order = None     # customer orders currently being worked (fixed at 1)
        self.n_quotes = 0              # number of quotes live on LOB
        self.willing = 1               # used in ZIP etc
        self.able = 1                  # used in ZIP etc
        self.birthtime = time          # used when calculating age of a trader/strategy
        self.profitpertime = 0         # profit per unit time
        self.n_trades = 0              # how many trades has this trader done?
        self.lastquote = None          # record of what its last quote was
        self.quantity_remaining = 0    # the quantity that has currently been traded from the last quote
        self.BI_threshold = 1          # the quantity threshold which determines when a BI should be used
        self.reputational_score = None # the last notified reputational score of the trader.


    def __str__(self):
        return '[TID %s type %s balance %s blotter %s customer order %s n_trades %s profitpertime %s]' \
            % (self.trader_id, self.ttype, self.balance, self.blotter, self.customer_order, self.n_trades, self.profitpertime)


    def add_order(self, customer_order, verbose):
        # in this version, trader has at most one order,
        # if allow more than one, this needs to be self.orders.append(order)
        if self.n_quotes > 0 :
            # this trader has a live quote on the LOB, from a previous customer order
            # need response to signal cancellation/withdrawal of that quote
            response = 'LOB_Cancel'
        else:
            response = 'Proceed'
        self.customer_order = customer_order
        if verbose : print('add_order < response=%s' % response)
        self.quantity_remaining = customer_order.quantity
        return response


    def del_order(self):
        # this is lazy: assumes each trader has only one customer order with quantity=1, so deleting sole order
        # CHANGE TO DELETE THE HEAD OF THE LIST AND KEEP THE TAIL
        self.customer_order = None


    def bookkeep(self, trade, verbose):

        outstr=str(self.customer_order)

        self.blotter.append(trade)  # add trade record to trader's blotter
        # NB What follows is **LAZY** -- assumes all orders are quantity=1
        transactionprice = trade['price']
        if self.customer_order.otype == 'Buy':
            profit = (self.customer_order.price - transactionprice) * trade['quantity']
        elif self.customer_order.otype == 'Sell':
            profit = (transactionprice - self.customer_order.price) * trade['quantity']
        self.balance += profit
        self.n_trades += 1
        self.profitpertime = self.balance/(trade['time'] - self.birthtime)

        if verbose: print('%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))

        # update the quantity remaining
        self.quantity_remaining -= trade['quantity']
        if self.quantity_remaining == 0:
            self.del_order()


    # specify how trader responds to events in the market
    # this is a null action, expect it to be overloaded by specific algos
    def respond(self, time, lob, trade, verbose):
        return None

    # specify how trader mutates its parameter values
    # this is a null action, expect it to be overloaded by specific algos
    def mutate(self, time, lob, trade, verbose):
        return None


# Trader subclass Giveaway
# even dumber than a ZI-U: just give the deal away
# (but never makes a loss)
class Trader_Giveaway(Trader):

    def getorder(self, time):
        # if the trader has no customer order then return None
        if self.customer_order == None:
            order = None

        elif self.quantity_remaining > 0:

            # if the quantity remaining is above the BI threshold then issue a block indication
            if self.quantity_remaining >= self.BI_threshold:

                MES = 100

                # create the block indication
                block_indication = Block_Indication(time,
                                                    self.trader_id,
                                                    self.customer_order.otype,
                                                    self.quantity_remaining,
                                                    self.customer_order.price,
                                                    MES)

                # update the lastquote member variable
                self.lastquote = block_indication

                # return the block indication
                return block_indication

            # otherwise issue a normal order
            else:

                MES = None

                # create the order
                order = Order(time, 
                              self.trader_id, 
                              self.customer_order.otype,
                              self.quantity_remaining,
                              self.customer_order.price,
                              MES)

                # update the last quote member variable
                self.lastquote=order

                #return the order
                return order

    # the trader recieves an Order Submission Request (OSR). The trader needs to respond with a
    # Qualifying Block Order (QBO) in order to confirm their block indication. 
    def get_qualifying_block_order(self, time, OSR):

        # Update the traders reputationa score
        self.reputational_score = OSR.reputational_score
        
        quantity = round(OSR.quantity * 0.5)
        limit_price = OSR.limit_price
        MES = OSR.MES

        # create a QBO from the received OSR
        QBO = Qualifying_Block_Order(time, 
                                     OSR.trader_id, 
                                     OSR.otype, 
                                     quantity,
                                     limit_price,
                                     MES, 
                                     OSR.match_id)
        # return the created QBO
        return QBO

    # if the block indication or the qualifying block order failed
    def BDS_failure(self, info):
        return


# This trader's behaviour is deterministic and is used for testing purposes
class Trader_Giveaway_test(Trader):

    def getorder(self, time):
        # if the trader has no customer order then return None
        if self.customer_order == None:
            order = None

        elif self.quantity_remaining > 0:

            # if the quantity remaining is above the BI threshold then issue a block indication
            if self.quantity_remaining >= self.BI_threshold:
            
                MES = 20

                # create the block indication
                block_indication = Block_Indication(time,
                                                    self.trader_id,
                                                    self.customer_order.otype,
                                                    self.quantity_remaining,
                                                    self.customer_order.price,
                                                    MES)

                # update the lastquote member variable
                self.lastquote = block_indication

                # return the block indication
                return block_indication

            # otherwise issue a normal order
            else:   
                
                MES = 2

                # create the order
                order = Order(time, 
                              self.trader_id, 
                              self.customer_order.otype, 
                              self.quantity_remaining,
                              self.customer_order.price,
                              MES)

                # update the last quote member variable
                self.lastquote=order

                #return the order
                return order

    # the trader recieves an Order Submission Request (OSR). The trader needs to respond with a
    # Qualifying Block Order (QBO) in order to confirm their block indication. 
    def get_qualifying_block_order(self, time, OSR):

        # Update the traders reputationa score
        self.reputational_score = OSR.reputational_score
        
        # If we are testing then use a deterministic quantity
        quantity = OSR.quantity - 10
        limit_price = OSR.limit_price
        MES = OSR.MES

        # create a QBO from the received OSR
        QBO = Qualifying_Block_Order(time, 
                                     OSR.trader_id, 
                                     OSR.otype, 
                                     quantity,
                                     limit_price,
                                     MES, 
                                     OSR.match_id)
        # return the created QBO
        return QBO

    # if the block indication or the qualifying block order failed
    def BDS_failure(self, info):
        return


##########################---Below lies the experiment/test-rig---##################



# trade_stats()
# dump CSV statistics on exchange data and trader population to file for later analysis
# this makes no assumptions about the number of types of traders, or
# the number of traders of any one type -- allows either/both to change
# between successive calls, but that does make it inefficient as it has to
# re-analyse the entire set of traders on each call
def trade_stats(expid, traders, dumpfile, time):

        # calculate the total balance sum for each type of trader and the number of each type of trader
        trader_types = {}
        n_traders = len(traders)
        for t in traders:
                ttype = traders[t].ttype
                if ttype in trader_types.keys():
                        t_balance = trader_types[ttype]['balance_sum'] + traders[t].balance
                        n = trader_types[ttype]['n'] + 1
                else:
                        t_balance = traders[t].balance
                        n = 1
                trader_types[ttype] = {'n':n, 'balance_sum':t_balance}

        # write the title for each column
        dumpfile.write('trial, time,')
        for i in range(0, len(trader_types)):
            dumpfile.write('type, total sum, n traders, avg\n')

        # write the trial number followed by the time
        dumpfile.write('%s, %06d, ' % (expid, time))
        # for each type of trader write: the type name, the total balance sum of all traders of that type,
        # the number of traders of that type, and then the average balance of each trader of that type
        for ttype in sorted(list(trader_types.keys())):
                n = trader_types[ttype]['n']
                s = trader_types[ttype]['balance_sum']
                dumpfile.write('%s, %d, %d, %f, ' % (ttype, s, n, s / float(n)))
        dumpfile.write('N, ')
        # write a new line
        dumpfile.write('\n');


# create a bunch of traders from traders_spec
# returns tuple (n_buyers, n_sellers)
# optionally shuffles the pack of buyers and the pack of sellers
def populate_market(traders_spec, traders, shuffle, verbose):

        # given a trader type and a name, create the trader
        def trader_type(robottype, name):
                if robottype == 'GVWY':
                        return Trader_Giveaway('GVWY', name, 0.00, 0)
                elif robottype == 'GVWY_test':
                        return Trader_Giveaway_test('GVWY', name, 0.00, 0)
                elif robottype == 'ZIC':
                        return Trader_ZIC('ZIC', name, 0.00, 0)
                elif robottype == 'SHVR':
                        return Trader_Shaver('SHVR', name, 0.00, 0)
                elif robottype == 'SNPR':
                        return Trader_Sniper('SNPR', name, 0.00, 0)
                elif robottype == 'ZIP':
                        return Trader_ZIP('ZIP', name, 0.00, 0)
                else:
                        sys.exit('FATAL: don\'t know robot type %s\n' % robottype)


        def shuffle_traders(ttype_char, n, traders):
                for swap in range(n):
                        t1 = (n - 1) - swap
                        t2 = random.randint(0, t1)
                        t1name = '%c%02d' % (ttype_char, t1)
                        t2name = '%c%02d' % (ttype_char, t2)
                        traders[t1name].trader_id = t2name
                        traders[t2name].trader_id = t1name
                        temp = traders[t1name]
                        traders[t1name] = traders[t2name]
                        traders[t2name] = temp

        # create the buyers from the specification and add them to the traders dictionary
        n_buyers = 0
        for bs in traders_spec['buyers']:
                ttype = bs[0]
                for b in range(bs[1]):
                        tname = 'B%02d' % n_buyers  # buyer i.d. string
                        traders[tname] = trader_type(ttype, tname)
                        traders[tname].BI_threshold = traders_spec['BI_threshold']
                        n_buyers = n_buyers + 1

        if n_buyers < 1:
                sys.exit('FATAL: no buyers specified\n')

        if shuffle: shuffle_traders('B', n_buyers, traders)

        # create the sellers from the specification and add them to the traders dictionary
        n_sellers = 0
        for ss in traders_spec['sellers']:
                ttype = ss[0]
                for s in range(ss[1]):
                        tname = 'S%02d' % n_sellers  # buyer i.d. string
                        traders[tname] = trader_type(ttype, tname)
                        traders[tname].BI_threshold = traders_spec['BI_threshold']
                        n_sellers = n_sellers + 1

        if n_sellers < 1:
                sys.exit('FATAL: no sellers specified\n')

        if shuffle: shuffle_traders('S', n_sellers, traders)

        # print the information about each trader
        if verbose :
                for t in range(n_buyers):
                        bname = 'B%02d' % t
                        print(traders[bname])
                for t in range(n_sellers):
                        bname = 'S%02d' % t
                        print(traders[bname])


        return {'n_buyers':n_buyers, 'n_sellers':n_sellers}


# customer_orders(): allocate orders to traders
# parameter "os" is order schedule
# os['timemode'] is either 'periodic', 'drip-fixed', 'drip-jitter', or 'drip-poisson'
# os['interval'] is number of seconds for a full cycle of replenishment
# drip-poisson sequences will be normalised to ensure time of last replenishment <= interval
# parameter "pending" is the list of future orders (if this is empty, generates a new one from os)
# revised "pending" is the returned value
#
# also returns a list of "cancellations": trader-ids for those traders who are now working a new order and hence
# need to kill quotes already on LOB from working previous order
#
#
# if a supply or demand schedule mode is "random" and more than one range is supplied in ranges[],
# then each time a price is generated one of the ranges is chosen equiprobably and
# the price is then generated uniform-randomly from that range
#
# if len(range)==2, interpreted as min and max values on the schedule, specifying linear supply/demand curve
# if len(range)==3, first two vals are min & max, third value should be a function that generates a dynamic price offset
#                   -- the offset value applies equally to the min & max, so gradient of linear sup/dem curve doesn't vary
# if len(range)==4, the third value is function that gives dynamic offset for schedule min,
#                   and fourth is a function giving dynamic offset for schedule max, so gradient of sup/dem linear curve can vary
#
# the interface on this is a bit of a mess... could do with refactoring

# the os dictionary parameter now contains a 'quantity_range' item
def customer_orders(time, last_update, traders, trader_stats, os, pending, verbose):


        def sysmin_check(price):
                if price < bse_sys_minprice:
                        print('WARNING: price < bse_sys_min -- clipped')
                        price = bse_sys_minprice
                return price


        def sysmax_check(price):
                if price > bse_sys_maxprice:
                        print('WARNING: price > bse_sys_max -- clipped')
                        price = bse_sys_maxprice
                return price

        
        # return the order price for trader i out of n by using the selected mode
        def getorderprice(i, sched, n, mode, issuetime):
                # does the first schedule range include optional dynamic offset function(s)?
                if len(sched[0]) > 2:
                        offsetfn = sched[0][2]
                        if callable(offsetfn):
                                # same offset for min and max
                                offset_min = offsetfn(issuetime)
                                offset_max = offset_min
                        else:
                                sys.exit('FAIL: 3rd argument of sched in getorderprice() not callable')
                        if len(sched[0]) > 3:
                                # if second offset function is specfied, that applies only to the max value
                                offsetfn = sched[0][3]
                                if callable(offsetfn):
                                        # this function applies to max
                                        offset_max = offsetfn(issuetime)
                                else:
                                        sys.exit('FAIL: 4th argument of sched in getorderprice() not callable')
                else:
                        offset_min = 0.0
                        offset_max = 0.0

                pmin = sysmin_check(offset_min + min(sched[0][0], sched[0][1]))
                pmax = sysmax_check(offset_max + max(sched[0][0], sched[0][1]))
                prange = pmax - pmin
                stepsize = prange / (n - 1)
                halfstep = round(stepsize / 2.0)

                if mode == 'fixed':
                        orderprice = pmin + int(i * stepsize) 
                elif mode == 'jittered':
                        orderprice = pmin + int(i * stepsize) + random.randint(-halfstep, halfstep)
                elif mode == 'random':
                        if len(sched) > 1:
                                # more than one schedule: choose one equiprobably
                                s = random.randint(0, len(sched) - 1)
                                pmin = sysmin_check(min(sched[s][0], sched[s][1]))
                                pmax = sysmax_check(max(sched[s][0], sched[s][1]))
                        orderprice = random.randint(pmin, pmax)
                else:
                        sys.exit('FAIL: Unknown mode in schedule')
                orderprice = sysmin_check(sysmax_check(orderprice))
                return orderprice


        # return a dictionary containing the issue times of orders according to the selected issuing mode
        def getissuetimes(n_traders, mode, interval, shuffle, fittointerval):
                interval = float(interval)
                if n_traders < 1:
                        sys.exit('FAIL: n_traders < 1 in getissuetime()')
                elif n_traders == 1:
                        tstep = interval
                else:
                        tstep = interval / (n_traders - 1)
                arrtime = 0
                issuetimes = []
                for t in range(n_traders):
                        if mode == 'periodic':
                                arrtime = interval
                        elif mode == 'drip-fixed':
                                arrtime = t * tstep
                        elif mode == 'drip-jitter':
                                arrtime = t * tstep + tstep * random.random()
                        elif mode == 'drip-poisson':
                                # poisson requires a bit of extra work
                                interarrivaltime = random.expovariate(n_traders / interval)
                                arrtime += interarrivaltime
                        else:
                                sys.exit('FAIL: unknown time-mode in getissuetimes()')
                        issuetimes.append(arrtime) 
                        
                # at this point, arrtime is the last arrival time
                if fittointerval and ((arrtime > interval) or (arrtime < interval)):
                        # generated sum of interarrival times longer than the interval
                        # squish them back so that last arrival falls at t=interval
                        for t in range(n_traders):
                                issuetimes[t] = interval * (issuetimes[t] / arrtime)
                # optionally randomly shuffle the times
                if shuffle:
                        for t in range(n_traders):
                                i = (n_traders - 1) - t
                                j = random.randint(0, i)
                                tmp = issuetimes[i]
                                issuetimes[i] = issuetimes[j]
                                issuetimes[j] = tmp
                return issuetimes
        

        # return a tuple containing the current ranges and stepmode      
        def getschedmode(time, os):
                got_one = False
                for sched in os:
                        if (sched['from'] <= time) and (time < sched['to']) :
                                # within the timezone for this schedule
                                schedrange = sched['price_ranges']
                                mode = sched['stepmode']
                                got_one = True
                                exit  # jump out the loop -- so the first matching timezone has priority over any others
                if not got_one:
                        sys.exit('Fail: time=%5.2f not within any timezone in os=%s' % (time, os))
                return (schedrange, mode)
        

        n_buyers = trader_stats['n_buyers']
        n_sellers = trader_stats['n_sellers']

        shuffle_times = True

        cancellations = []

        # if there are no pending orders
        if len(pending) < 1:
                # list of pending (to-be-issued) customer orders is empty, so generate a new one
                new_pending = []

                # add the demand side (buyers) customer orders to the list of pending orders
                issuetimes = getissuetimes(n_buyers, os['timemode'], os['interval'], shuffle_times, True)
                ordertype = 'Buy'
                (sched, mode) = getschedmode(time, os['dem'])             
                for t in range(n_buyers):
                        issuetime = time + issuetimes[t]
                        tname = 'B%02d' % t
                        orderprice = getorderprice(t, sched, n_buyers, mode, issuetime)
                        # generating a random order quantity
                        quantity_min = os['quantity_range'][0]
                        quantity_max = os['quantity_range'][1]
                        quantity = random.randint(quantity_min,quantity_max)
                        customer_order = Customer_Order(issuetime, tname, ordertype, orderprice, quantity)
                        new_pending.append(customer_order)
                        
                # add the supply side (sellers) customer orders to the list of pending orders
                issuetimes = getissuetimes(n_sellers, os['timemode'], os['interval'], shuffle_times, True)
                ordertype = 'Sell'
                (sched, mode) = getschedmode(time, os['sup'])
                for t in range(n_sellers):
                        issuetime = time + issuetimes[t]
                        tname = 'S%02d' % t
                        orderprice = getorderprice(t, sched, n_sellers, mode, issuetime)
                        # generating a random order quantity
                        quantity_min = os['quantity_range'][0]
                        quantity_max = os['quantity_range'][1]
                        quantity = random.randint(quantity_min,quantity_max)
                        customer_order = Customer_Order(issuetime, tname, ordertype, orderprice, quantity)
                        new_pending.append(customer_order)
        # if there are some pending orders
        else:
                # there are pending future orders: issue any whose timestamp is in the past
                new_pending = []
                for order in pending:
                        if order.time < time:
                                # this order should have been issued by now
                                # issue it to the trader
                                tname = order.trader_id
                                response = traders[tname].add_order(order, verbose)
                                if verbose: print('Customer order: %s %s' % (response, order) )
                                # if issuing the order causes the trader to cancel their current order then add
                                # the traders name to the cancellations list
                                if response == 'LOB_Cancel' :
                                    cancellations.append(tname)
                                    if verbose: print('Cancellations: %s' % (cancellations))
                                # and then don't add it to new_pending (i.e., delete it)
                        else:
                                # this order stays on the pending list
                                new_pending.append(order)
        return [new_pending, cancellations]

# one session in the market
# This was modified to work with the dark pool
def market_session(sess_id, starttime, endtime, trader_spec, order_schedule, dumpfile, dump_each_trade):

    # variables which dictate what information is printed to the output
    verbose = False
    traders_verbose = False
    orders_verbose = False
    lob_verbose = False
    process_verbose = False
    respond_verbose = False
    bookkeep_verbose = False


    # initialise the exchange
    exchange = Exchange()
    exchange.block_indication_book.MIV = 600


    # create a bunch of traders
    traders = {}
    trader_stats = populate_market(trader_spec, traders, True, traders_verbose)


    # timestep set so that can process all traders in one second
    # NB minimum interarrival time of customer orders may be much less than this!! 
    timestep = 1.0 / float(trader_stats['n_buyers'] + trader_stats['n_sellers'])
    
    duration = float(endtime - starttime)

    last_update = -1.0

    time = starttime

    # this list contains all the pending customer orders that are yet to happen
    pending_cust_orders = []

    print('\n%s;  ' % (sess_id))

    while time < endtime:

        # how much time left, as a percentage?
        time_left = (endtime - time) / duration

        if verbose: print('%s; t=%08.2f (%4.1f/100) ' % (sess_id, time, time_left*100))

        trade = None

        # update the pending customer orders list by generating new orders if none remain and issue 
        # any customer orders that were scheduled in the past. Note these are customer orders being
        # issued to traders, quotes will not be put onto the exchange yet
        [pending_cust_orders, kills] = customer_orders(time, last_update, traders, trader_stats,
                                         order_schedule, pending_cust_orders, orders_verbose)

        # if any newly-issued customer orders mean quotes on the LOB need to be cancelled, kill them
        if len(kills) > 0 :
            if verbose : print('Kills: %s' % (kills))
            for kill in kills :
                if verbose : print('lastquote=%s' % traders[kill].lastquote)
                if traders[kill].lastquote != None :
                    if verbose : print('Killing order %s' % (str(traders[kill].lastquote)))
                    exchange.del_order(time, traders[kill].lastquote, verbose)


        # get a limit-order quote (or None) from a randomly chosen trader
        tid = list(traders.keys())[random.randint(0, len(traders) - 1)]
        order = traders[tid].getorder(time)

        if verbose: print('Trader Quote: %s' % (order))

        # if the randomly selected trader gives us a quote, then add it to the exchange
        if order != None:

            # add the order to the exchange
            if isinstance(order, Order):
                result = exchange.add_order(order, process_verbose)

            # add block indication to the exchange and find matches
            elif isinstance(order, Block_Indication):
                result = exchange.add_block_indication(order, process_verbose)
                exchange.match_block_indications_and_get_firm_orders(time, traders, 50)
            traders[tid].n_quotes = 1

            # execute all possible trades
            trades = exchange.execute_trades(time, 50)

            # trades occurred, so the counterparties update order lists and blotters
            for trade in trades:
                traders[trade['buyer']].bookkeep(trade, bookkeep_verbose)
                traders[trade['seller']].bookkeep(trade, bookkeep_verbose)

        time = time + timestep

    # print the final order and block indications
    print("Final orders and block indications:")
    exchange.print_order_book()
    exchange.print_block_indications()
    exchange.print_matches()

    # end of an experiment -- dump the tape
    exchange.tape_dump('output/transactions_dark.csv', 'w', 'keep')
    # dump the traders' reputational score history
    exchange.composite_reputational_scores_history_dump('output/composite_reputational_scores_history.csv', 'w', 'keep')
    exchange.event_reputational_scores_dump('output/event_reputational_scores.csv', 'w', 'keep')

    # write trade_stats for this experiment NB end-of-session summary only
    trade_stats(sess_id, traders, dumpfile, time)


def experiment1():

    start_time = 0.0
    end_time = 600.0
    duration = end_time - start_time

    price_range1 = (25, 45)
    supply_schedule = [ {'from':start_time, 'to':end_time, 'price_ranges':[price_range1], 'stepmode':'fixed'}
                      ]

    price_range1 = (55, 75)
    demand_schedule = [ {'from':start_time, 'to':end_time, 'price_ranges':[price_range1], 'stepmode':'fixed'}
                      ]

    order_sched = {'sup':supply_schedule, 'dem':demand_schedule,
                   'interval':30, 'timemode':'drip-fixed', 'quantity_range':[1,1000]}

    buyers_spec = [('GVWY',20)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec, 'BI_threshold':900}

    n_trials = 1
    tdump=open('output/avg_balance_dark.csv','w')
    trial = 1
    if n_trials > 1:
            dump_all = False
    else:
            dump_all = True
            
    while (trial<(n_trials+1)):
            trial_id = 'trial%04d' % trial
            market_session(trial_id, start_time, end_time, traders_spec, order_sched, tdump, dump_all)
            tdump.flush()
            trial = trial + 1
    tdump.close()

    sys.exit('Done Now')

def experiment2():

    start_time = 0.0
    end_time = 10000.0
    duration = end_time - start_time

    price_range1 = (25, 45)
    supply_schedule = [ {'from':start_time, 'to':end_time, 'price_ranges':[price_range1], 'stepmode':'fixed'}
                      ]

    price_range1 = (55, 75)
    demand_schedule = [ {'from':start_time, 'to':end_time, 'price_ranges':[price_range1], 'stepmode':'fixed'}
                      ]

    order_sched = {'sup':supply_schedule, 'dem':demand_schedule,
                   'interval':30, 'timemode':'drip-fixed', 'quantity_range':[1,1000]}

    buyers_spec = [('GVWY',20)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec, 'BI_threshold':900}

    n_trials = 1
    tdump=open('output/avg_balance_dark.csv','w')
    trial = 1
    if n_trials > 1:
            dump_all = False
    else:
            dump_all = True
            
    while (trial<(n_trials+1)):
            trial_id = 'trial%04d' % trial
            market_session(trial_id, start_time, end_time, traders_spec, order_sched, tdump, dump_all)
            tdump.flush()
            trial = trial + 1
    tdump.close()

    sys.exit('Done Now')

# the main function is called if BSE.py is run as the main program
if __name__ == "__main__":
    experiment2()