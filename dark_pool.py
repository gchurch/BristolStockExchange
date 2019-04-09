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
        return 'Customer Order [T=%5.2f %s %s P=%s Q=%s]' % (self.time, self.trader_id, self.otype, self.price, self.quantity)


#######################-Order Class-################################


# an order created by a trader for the exchange
class Order:

    def __init__(self, time, trader_id, otype, quantity, MES):
        self.id = -1       # order i.d. (unique to each order on the Exchange)
        self.time = time    # timestamp
        self.trader_id = trader_id      # trader i.d.
        self.otype = otype  # order type
        self.quantity = quantity      # quantity
        self.MES = MES      # minimum execution size

    def __str__(self):
        return 'Order: [ID=%d T=%5.2f %s %s Q=%s MES=%s]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.MES)


######################-Block_Indication Class-#######################################


# a block indication created by a trader for the exchange
class Block_Indication:

    def __init__(self, time, trader_id, otype, quantity, MES):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.MES = MES

    def __str__(self):
        return 'BI: [ID=%d T=%5.2f %s %s Q=%s MES=%s]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.MES)


#########################-Order Submission Request Class-############################

# a Order Submission Request (OSR) sent to a trader when their block indication is matched
class Order_Submission_Request:

    def __init__(self, time, trader_id, otype, quantity, MES, match_id):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.MES = MES
        self.match_id = match_id

    def __str__(self):
        return 'OSR: [ID=%d T=%5.2f %s %s Q=%s MES=%s MID=%d]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.MES, self.match_id)


#########################-Qualifying_Block_Order Class-###############################

# a Qualifying Block Order (QBO) created by a trader for the exchange
class Qualifying_Block_Order:

    def __init__(self, time, trader_id, otype, quantity, MES, match_id):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.MES = MES
        self.match_id = match_id

    def __str__(self):
        return 'QBO: [ID=%d T=%5.2f %s %s Q=%s MES=%s MID=%d]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.MES, self.match_id)


########################-Orderbook_half Class-#################


# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first
class Orderbook_half:

    def __init__(self, booktype):
        # booktype: bids or asks?
        self.booktype = booktype
        # a dictionary containing all traders and the number of orders they have in this order book
        self.traders = {}
        # list of orders received, sorted by size and then time
        self.orders = []
        # number of current orders
        self.num_orders = 0

    # find the position to insert the order into the order_book list such that the order_book list maintains
    # it's ordering of (size,time)
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

    # add the order to the orders dictionary and to the order_book list
    def book_add(self, order):

        # if the trader with this tid already has an order in the order_book, then remove it
        # also set the write reponse to return
        if self.traders.get(order.trader_id) != None:
            self.book_del(order.trader_id)
            response = 'Overwrite'
        else:
            response = 'Addition'

        # Note. changing the order in the order_book list will also change the order in the orders dictonary
        
        # add the trader to the traders dictionary
        num_orders = self.num_orders
        self.traders[order.trader_id] = 1
        self.num_orders = len(self.traders)

        # add the order to order_book list
        position = self.find_order_position(order)
        self.orders.insert(position, order)

        # return whether this was an addition or an overwrite
        return response

    # delete the order by the trader with the given tid
    def book_del(self, tid):
        del(self.traders[tid])
        
        # calling pop changes the length of order_book so we have to break afterwards
        for i in range(0, len(self.orders)):
            if self.orders[i].trader_id == tid:
                self.orders.pop(i)
                break

        self.num_orders = len(self.orders)

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

    # add an order to the order book
    def add_order(self, order, verbose):
        # add a order to the exchange and update all internal records; return unique i.d.
        order.id = self.order_id
        self.order_id = order.id + 1
        # if verbose : print('QUID: order.quid=%d self.quote.id=%d' % (order.id, self.order_id))
        if order.otype == 'Buy':
            response=self.buy_side.book_add(order)
        else:
            response=self.sell_side.book_add(order)
        return [order.id, response]

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


    # match two orders and perform the trade
    def find_matching_orders(self):

        # matching is buy-side friendly, so start with buys first
        for buy_order in self.buy_side.orders:
            for sell_order in self.sell_side.orders:
                # find two matching orders in the order_book list
                if buy_order.quantity >= sell_order.MES and buy_order.MES <= sell_order.quantity:
                    # work out how large the trade size will be
                    if buy_order.quantity >= sell_order.quantity:
                        trade_size = sell_order.quantity
                    else:
                        trade_size = buy_order.quantity
                    # return a dictionary containing the trade info
                    # Note. Here we are returning references to the orders, so changing the returned orders will
                    # change the orders in the order_book
                    return {"buy_order": buy_order, "sell_order": sell_order, "trade_size": trade_size}

        # if no match can be found, return None
        return None

    # given a buy order, a sell order and a trade size, perform the trade
    def perform_trade(self, traders, time, price, trade_info):

        # subtract the trade quantity from the orders' quantity
        trade_info["buy_order"].quantity -= trade_info["trade_size"]
        trade_info["sell_order"].quantity -= trade_info["trade_size"]

        # remove orders from the order_book
        self.buy_side.book_del(trade_info["buy_order"].trader_id)
        self.sell_side.book_del(trade_info["sell_order"].trader_id)

        # re-add the the residual
        if trade_info["buy_order"].quantity > 0:
            # update the MES if necessary
            if trade_info["buy_order"].MES > trade_info["buy_order"].quantity:
                trade_info["buy_order"].MES = trade_info["buy_order"].quantity
            # add the order to the order_book list
            self.buy_side.book_add(trade_info["buy_order"])

        # re-add the residual
        if trade_info["sell_order"].quantity > 0:
            # update the MES if necessary
            if trade_info["sell_order"].MES > trade_info["sell_order"].quantity:
                trade_info["sell_order"].MES = trade_info["sell_order"].quantity
            # add the order to the order_book list
            self.sell_side.book_add(trade_info["sell_order"])

        # create a record of the transaction to the tape
        trade = {   'type': 'Trade',
                    'time': time,
                    'price': price,
                    'quantity': trade_info["trade_size"],
                    'buyer': trade_info["buy_order"].trader_id,
                    'seller': trade_info["sell_order"].trader_id}

        # the traders parameter may be set to none when we are just trying to test the uncross function
        if traders != None:
            # inform the traders of the trade
            traders[trade_info["buy_order"].trader_id].bookkeep(trade, False)
            traders[trade_info["sell_order"].trader_id].bookkeep(trade, False)

        # add a record to the tape
        self.tape.append(trade)

    # write the tape to an output file
    def tape_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        # write the title for each column
        dumpfile.write('time, buyer, seller, quantity, price\n')
        # write the information for each trade
        for tapeitem in self.tape:
            if tapeitem['type'] == 'Trade' :
                dumpfile.write('%s, %s, %s, %s, %s\n' % (tapeitem['time'], tapeitem['buyer'], tapeitem['seller'], tapeitem['quantity'], tapeitem['price']))
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
        # the buy side contains all of the block indications to buy
        self.buy_side = Orderbook_half('Buy')
        # the sell side contains all of the block indications to sell
        self.sell_side = Orderbook_half('Sell')
        # ID to be given to next block indication
        self.BI_id = 0
        # the reputational_scores dictionary contains the reputation score for each trader TID. The score will be
        # between 0 and 100
        self.reputational_scores = {}
        # the reputational score threshold (RST). All traders with a reputational score below this threshold
        # are no longer able to use the block discovery service
        self.RST = 20
        # The minimum indication value (MIV) is the quantity that a block indication must be greater
        # than in order to be accepted
        self.MIV = 20
        # A dictionary to hold matched BIs and the corresponding QBOs
        self.matches = {}
        # ID to be given to next Qualifying Block Order received
        self.QBO_id = 0
        # ID to be given to the matching of two block indications
        self.match_id = 0
        # The tape contains the history of block indications sent to the exchange
        self.tape = []
        # ID to be given to the next OSR created
        self.OSR_id = 0

    
    # add block indication
    def add_block_indication(self, BI, verbose):

        # if a new trader, then give it an initial reputational score
        if self.reputational_scores.get(BI.trader_id) == None:
            self.reputational_scores[BI.trader_id] = 50

        # the quantity of the order must be greater than the MIV
        if BI.quantity > self.MIV and self.reputational_scores.get(BI.trader_id) > self.RST:

            # set the block indications' id
            BI.id = self.BI_id
            self.BI_id = BI.id + 1

            # add the block indication to the correct order book
            if BI.otype == 'Buy':
                response=self.buy_side.book_add(BI)
            else:
                response=self.sell_side.book_add(BI)

            # return the order id and the response
            return [BI.id, response]

        # if the quantity of the order was not greater than the MIV then return a message
        return "Block Indication Rejected"

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
            # neither bid nor ask?
            sys.exit('bad order type in del_quote()')

    # attempt to find two matching block indications
    def find_matching_block_indications(self):
        # starting with the buy side first
        for buy_side_BI in self.buy_side.orders:
            for sell_side_BI in self.sell_side.orders:
                # check if the two block indications match
                if buy_side_BI.quantity >= sell_side_BI.MES and buy_side_BI.MES <= sell_side_BI.quantity:
                    
                    # Add the BIs in the match to the matches dictionary
                    self.matches[self.match_id] = {"buy_side_BI": buy_side_BI, 
                                                   "sell_side_BI": sell_side_BI,
                                                   "buy_side_QBO": None,
                                                   "sell_side_QBO": None}
                    # get the current match id
                    response = self.match_id

                    # increment the book's match_id counter
                    self.match_id += 1

                    # delete these block indications from the book
                    self.del_block_indication(100.0, buy_side_BI, False)
                    self.del_block_indication(100.0, sell_side_BI, False)

                    # return the match id
                    return response
        # if no match was found then return None
        return None

    def get_block_indication_match(self, match_id):
        return self.matches.get(match_id)

    # add a Qualifying Block Order (QBO). QBOs are added to the appropriate entry in the matches dictionary.
    def add_qualifying_block_order(self, QBO, verbose):

        # give each qualifying block order its own unique id
        QBO.id = self.QBO_id
        self.QBO_id += 1

        # get the match id for the orginally matched block indications
        match_id = QBO.match_id

        # and the order to the qualifying_block_orders dictionary with the key as match_id
        if self.matches.get(match_id) != None:
            if QBO.otype == 'Buy':
                self.matches[match_id]["buy_side_QBO"] = QBO
            elif QBO.otype == "Sell":
                self.matches[match_id]["sell_side_QBO"] = QBO
        else:
            return "Incorrect match id."
        
        # check if both QBOs have been received
        if self.matches[match_id]["buy_side_QBO"] and self.matches[match_id]["sell_side_QBO"]:
            return "Both QBOs have been received."
        else:
            return "First QBO received."

    # calculate the reputational score of a trader for a single event
    def calculate_event_reputational_score(self, QBO, BI):

        # if the QBO's MES is greater than the BI's MES then it is not "marketable" so give score zero
        if QBO.MES > BI.MES:
            return 0

        # calculate the score for this event
        score = 100
        MES_percent_diff = 100 * (BI.MES - QBO.MES) / BI.MES
        quantity_percent_diff = 100 * (BI.quantity - QBO.quantity) / BI.quantity
        score = 100 - MES_percent_diff - quantity_percent_diff
        if score > 100: score = 100
        if score < 50: score = 50

        # return the score
        return score

    # update both traders' reputation score given this matching event
    def update_reputational_scores(self, match_id):

        # the QBO and BI for the buy side
        buy_side_BI = self.matches[match_id]["buy_side_BI"]
        sell_side_BI = self.matches[match_id]["sell_side_BI"]
        buy_side_QBO = self.matches[match_id]["buy_side_QBO"]
        sell_side_QBO = self.matches[match_id]["sell_side_QBO"]

        # get the event reputation scores
        buy_side_event_score = self.calculate_event_reputational_score(buy_side_QBO, buy_side_BI)
        sell_side_event_score = self.calculate_event_reputational_score(sell_side_QBO, sell_side_QBO)

        # update the traders' reputational score
        self.update_trader_reputational_score(buy_side_BI.trader_id, buy_side_event_score)
        self.update_trader_reputational_score(sell_side_BI.trader_id, sell_side_event_score)

    # update a traders reputational score given an event_score
    def update_trader_reputational_score(self, tid, event_score):
        self.reputational_scores[tid] = self.reputational_scores[tid] * 0.75 + event_score * 0.25

    def delete_match(self, match_id):
        del(self.matches[match_id])

    def create_order_submission_requests(self, match_id):
        buy_side_BI = self.get_block_indication_match(match_id)["buy_side_BI"]
        sell_side_BI = self.get_block_indication_match(match_id)["sell_side_BI"]
        
        # create the OSRs
        buy_side_OSR = Order_Submission_Request(buy_side_BI.time,
                                                buy_side_BI.trader_id,
                                                buy_side_BI.otype,
                                                buy_side_BI.quantity,
                                                buy_side_BI.MES,
                                                match_id)
        buy_side_OSR.id = self.OSR_id
        self.OSR_id += 1
        sell_side_OSR = Order_Submission_Request(sell_side_BI.time,
                                                 sell_side_BI.trader_id,
                                                 sell_side_BI.otype,
                                                 sell_side_BI.quantity,
                                                 sell_side_BI.MES,
                                                 match_id)
        sell_side_OSR.id = self.OSR_id
        self.OSR_id += 1

        # return both OSRs
        return {"buy_side_OSR": buy_side_OSR, "sell_side_OSR": sell_side_OSR}

    # print the reputational score of all known traders
    def print_reputational_scores(self):
        print("Reputational scores:")
        for key in self.reputational_scores:
            print("%s : %d" % (key, self.reputational_scores[key]))
        print("")

    # print the current traders with block indications
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
            print(self.matches[key]["buy_side_BI"])
            print(self.matches[key]["sell_side_BI"])
            if self.matches[key]["buy_side_QBO"]:
                print(self.matches[key]["buy_side_QBO"])
            if self.matches[key]["sell_side_QBO"]:
                print(self.matches[key]["sell_side_QBO"])
        print("")


####################-Exchange Class-################################


# Exchange class
class Exchange:

    # constructor method
    def __init__(self):
        self.order_book = Orderbook()
        self.block_indications = Block_Indication_Book()

    # add an order to the exchange
    def add_order(self, order, verbose):
        if(isinstance(order, Order)):
            return self.order_book.add_order(order, verbose)
        else:
            return "Not an Order."
    
    def add_block_indication(self, BI, verbose):
        if(isinstance(BI, Block_Indication)):
            return self.block_indications.add_block_indication(BI, verbose)
        else:
            return "Not a Block Indication."

    def add_qualifying_block_order(self, QBO, verbose):
        if(isinstance(QBO, Qualifying_Block_Order)):
            return self.block_indications.add_qualifying_block_order(QBO, verbose)
        else:
            return "Not a Qualifying Block Order."


    # delete an order from the exchange
    def del_order(self, time, order, verbose):
        return self.order_book.del_order(time, order, verbose)

    # this function executes the uncross event, trades occur at the given time at the given price
    # keep making trades out of matching order until no more matches can be found
    def uncross(self, traders, time, price):

        # find a match between a buy order a sell order
        match_info = self.order_book.find_matching_orders()

        # keep on going until no more matches can be found
        while match_info != None:

            # execute the trade with the matched orders
            self.order_book.perform_trade(traders, time, 50.0, match_info)

            # find another match
            match_info = self.order_book.find_matching_orders()

    def del_block_indication(self, time, order, verbose):
        response = self.block_indications.del_block_indication(time, order, verbose)
        return response

    # write the order_book's tape to the output file
    def tape_dump(self, fname, fmode, tmode):
        self.order_book.tape_dump(fname, fmode, tmode)


    def find_matching_block_indications(self):
        return self.block_indications.find_matching_block_indications()

    def get_block_indication_match(self, match_id):
        return self.block_indications.get_block_indication_match(match_id)

    def delete_block_indication_match(self, match_id):
        return self.block_indications.delete_match(match_id)

    def update_reputational_scores(self, match_id):
        return self.block_indications.update_reputational_scores(match_id)

    def add_firm_orders_to_order_book(self, match_id):
        full_match = self.get_block_indication_match(match_id)
        buy_side_QBO = full_match["buy_side_QBO"]
        sell_side_QBO = full_match["sell_side_QBO"]

        # create orders out of the QBOs
        buy_side_order = Order(buy_side_QBO.time,
                               buy_side_QBO.trader_id,
                               buy_side_QBO.otype,
                               buy_side_QBO.quantity,
                               buy_side_QBO.MES)
        sell_side_order = Order(sell_side_QBO.time,
                                sell_side_QBO.trader_id,
                                sell_side_QBO.otype,
                                sell_side_QBO.quantity,
                                sell_side_QBO.MES)
        self.add_order(buy_side_order, False)
        self.add_order(sell_side_order, False)

    def create_order_submission_requests(self, match_id):
        return self.block_indications.create_order_submission_requests(match_id)

    # print the current orders in the orders dictionary
    def print_traders(self):
        self.order_book.print_traders()

    # print the current orders in the order_book list
    def print_order_book(self):
        self.order_book.print_order_book()

    def print_block_indication_traders(self):
        self.block_indications.print_block_indication_traders()

    def print_block_indications(self):
        self.block_indications.print_block_indications()

    def print_reputational_scores(self):
        self.block_indications.print_reputational_scores()

    def print_qualifying_block_orders(self):
        self.block_indications.print_qualifying_block_orders()

    def print_matches(self):
        self.block_indications.print_matches()


##################--Traders below here--#############


# Trader superclass
# all Traders have a trader id, bank balance, blotter, and list of orders to execute
class Trader:

    def __init__(self, ttype, tid, balance, time):
        self.ttype = ttype             # what type / strategy this trader is
        self.trader_id = tid                 # trader unique ID code
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
        return response


    def del_order(self, order):
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
        else:
            profit = (transactionprice - self.customer_order.price) * trade['quantity']
        self.balance += profit
        self.n_trades += 1
        self.profitpertime = self.balance/(trade['time'] - self.birthtime)

        if verbose: print('%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))


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
        if self.customer_order == None:
            order = None
        elif self.customer_order.quantity >= 20:
            MES = 20
            # return a block indication
            block_indication = Block_Indication(time, self.trader_id, self.customer_order.otype, self.customer_order.quantity, MES)
            return block_indication
        else:
            MES = 2
            order = Order(time, self.trader_id, self.customer_order.otype, self.customer_order.quantity, MES)
            self.lastquote=order
            return order

    # the trader recieves an Order Submission Request (OSR). The trader needs to respond with a
    # Qualifying Block Order (QBO) in order to confirm their block indication
    # Currently we are sending a QBO with the same quantity as in the BI
    def order_submission_request(self, time, OSR):
        # create a QOB from the received OSR
        MES = 20
        QOB = Qualifying_Block_Order(time, 
                                     OSR.trader_id, 
                                     OSR.otype, 
                                     OSR.quantity, 
                                     MES, 
                                     OSR.match_id)
        # return the created QOB
        return QOB



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
            dumpfile.write('type, sum, n, avg\n')

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


def match_block_indications_and_add_firm_orders_to_the_order_book(exchange, traders):
    # check if there is a match between any two block indications
    match_id = exchange.find_matching_block_indications()

    # if there is a match then go through all of the necessary steps
    if match_id != None:

        # get the block indications that were matched
        full_match = exchange.get_block_indication_match(match_id)
        buy_side_BI = full_match["buy_side_BI"]
        sell_side_BI = full_match["sell_side_BI"]

        # send OSR to the traders and get back QBOs for the matched BIs
        OSRs = exchange.create_order_submission_requests(match_id)
        buy_side_qbo = traders[buy_side_BI.trader_id].order_submission_request(100.0, OSRs["buy_side_OSR"])
        sell_side_qbo = traders[sell_side_BI.trader_id].order_submission_request(100.0, OSRs["sell_side_OSR"])

        # add the QBOs to the exchange
        exchange.add_qualifying_block_order(buy_side_qbo, False)
        exchange.add_qualifying_block_order(sell_side_qbo, False)

        # update the reputational scores of the traders in the match
        exchange.update_reputational_scores(match_id)
        # add the firm orders to the order book.
        exchange.add_firm_orders_to_order_book(match_id)
        # delete the block indication match
        # exchange.delete_block_indication_match(match_id)

        return "Match found."
    return "No match found."

# perform a test with the dark pool
def test():

    # initialise the exchange
    exchange = Exchange()

    # create the trader specs
    buyers_spec = [('GVWY',12)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec}

    # create a bunch of traders
    traders = {}
    trader_stats = populate_market(traders_spec, traders, True, False)

    # create some customer orders
    customer_orders = []
    customer_orders.append(Customer_Order(25.0, 'B00', 'Buy', 100, 5,))
    customer_orders.append(Customer_Order(35.0, 'B01', 'Buy', 100, 10))
    customer_orders.append(Customer_Order(55.0, 'B02', 'Buy', 100, 3))
    customer_orders.append(Customer_Order(75.0, 'B03', 'Buy', 100, 32))
    customer_orders.append(Customer_Order(25.0, 'B04', 'Buy', 100, 5,))
    customer_orders.append(Customer_Order(35.0, 'B05', 'Buy', 100, 10))
    customer_orders.append(Customer_Order(55.0, 'B06', 'Buy', 100, 3))
    customer_orders.append(Customer_Order(65.0, 'B07', 'Buy', 100, 52))
    customer_orders.append(Customer_Order(25.0, 'B08', 'Buy', 100, 5,))
    customer_orders.append(Customer_Order(35.0, 'B09', 'Buy', 100, 10))
    customer_orders.append(Customer_Order(55.0, 'B10', 'Buy', 100, 3))
    customer_orders.append(Customer_Order(45.0, 'B11', 'Buy', 100, 25))
    customer_orders.append(Customer_Order(45.0, 'S00', 'Sell', 0, 11))
    customer_orders.append(Customer_Order(55.0, 'S01', 'Sell', 0, 4))
    customer_orders.append(Customer_Order(60.0, 'S02', 'Sell', 0, 12))
    customer_orders.append(Customer_Order(65.0, 'S03', 'Sell', 0, 46))
    customer_orders.append(Customer_Order(45.0, 'S04', 'Sell', 0, 11))
    customer_orders.append(Customer_Order(55.0, 'S05', 'Sell', 0, 4))
    customer_orders.append(Customer_Order(60.0, 'S06', 'Sell', 0, 12))
    customer_orders.append(Customer_Order(55.0, 'S07', 'Sell', 0, 52))
    customer_orders.append(Customer_Order(45.0, 'S08', 'Sell', 0, 11))
    customer_orders.append(Customer_Order(55.0, 'S09', 'Sell', 0, 4))
    customer_orders.append(Customer_Order(60.0, 'S10', 'Sell', 0, 12))
    customer_orders.append(Customer_Order(75.0, 'S11', 'Sell', 0, 31))

    # assign customer orders to traders
    for customer_order in customer_orders:
        traders[customer_order.trader_id].add_order(customer_order, False)

    for tid in sorted(traders.keys()):
        print(tid)


    # add each trader's order to the exchange
    for tid in sorted(traders.keys()):
        order = traders[tid].getorder(20.0)
        if order != None:
            if isinstance(order, Order):
                exchange.add_order(order, False)
            elif isinstance(order, Block_Indication):
                exchange.add_block_indication(order, False)
                # check if there is a match between block indications
                if match_block_indications_and_add_firm_orders_to_the_order_book(exchange, traders) == "Match found.":
                    print("before:")
                    exchange.print_order_book()
                    # if there is a match then start trading
                    exchange.uncross(traders, 100.0, 50)
                    print("after:")
                    exchange.print_order_book()

    exchange.print_matches() 


    # dump the trading data
    exchange.tape_dump('transactions_dark.csv', 'w', 'keep')



# the main function is called if BSE.py is run as the main program
if __name__ == "__main__":
    test()