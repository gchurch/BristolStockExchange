from orders import *

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


# Modified Giveaway Trader
class Trader_BDS_Giveaway(Trader):

    def getorder(self, time):
        # if the trader has no customer order then return None
        if self.customer_order == None:
            order = None

        elif self.quantity_remaining > 0:

            # if the quantity remaining is above the BI threshold then issue a block indication
            if self.quantity_remaining >= self.BI_threshold:

                # the minimum execution size for the order
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

                # the minimum exeuction size for the order
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

                # return the order
                return order

    # the trader recieves an Order Submission Request (OSR). The trader needs to respond with a
    # Qualifying Block Order (QBO) in order to confirm their block indication. 
    def get_qualifying_block_order(self, time, OSR):

        # Update the traders reputationa score
        self.reputational_score = OSR.reputational_score
        
        quantity = OSR.quantity * 0.5
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
class Trader_BDS_Giveaway_test(Trader):

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
        quantity = OSR.quantity - 100
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
