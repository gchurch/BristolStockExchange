import sys
import math
import random
import copy


bse_sys_minprice = 1  # minimum price in the system, in cents/pennies
bse_sys_maxprice = 1000  # maximum price in the system, in cents/pennies
ticksize = 1  # minimum change in price, in cents/pennies

# a customer order which is given to a trader to complete
class Customer_Order:

    def __init__(self, tid, otype, price, qty, time):
        self.tid = tid        # the trader i.d. that this order is for
        self.otype = otype    # the order type of the customer order i.e. buy/sell
        self.price = price    # the limit price of the customer order
        self.qty = qty        # the quantity to buy/sell
        self.time = time      # the time the customer order was issued



# an order put forward by a trader for the exchange
class Order:

    def __init__(self, tid, otype, qty, MES, time):
        self.tid = tid      # trader i.d.
        self.otype = otype  # order type
        self.qty = qty      # quantity
        self.MES = MES      # minimum execution size
        self.time = time    # timestamp
        self.oid = -1       # order i.d. (unique to each order on the Exchange)

    def __str__(self):
        return '[%s %s Q=%s MES=%s T=%5.2f OID:%d]' % (self.tid, self.otype, self.qty, self.MES, self.time, self.oid)


# Orderbook_half is one side of the book: a list of bids or a list of asks, each sorted best-first

class Orderbook_half:

    def __init__(self, booktype):
        # booktype: bids or asks?
        self.booktype = booktype
        # a dictionary of the the original orders placed in the orderbook
        self.orders = {}
        # list of orders received, sorted by size and then time
        self.order_book = []
        # summary stats
        self.n_orders = 0  # how many orders?

    # find the position to insert the order into the order_book list such that the order_book list maintains
    # it's ordering of (size,time)
    def find_order_book_position(self, order):
        quantity = order.qty
        time = order.time
        position = 0
        for i in range(0,len(self.order_book)):
            if quantity > self.order_book[i].qty or (quantity == self.order_book[i].qty and time < self.order_book[i].time):
                break
            else:
                position += 1
        return position

    # remove all orders on the order book from the trader with the givin tid
    def remove_from_order_book(self, tid):

        # calling pop changes the length of order_book so we have to break afterwards
        for i in range(0, len(self.order_book)):
            if self.order_book[i].tid == tid:
                self.order_book.pop(i)
                break

    # add the order to the orders dictionary and to the order_book list
    def book_add(self, order):

        # if the trader with this tid already has an order in the order_book, then remove it
        if self.orders.get(order.tid) != None:
            self.remove_from_order_book(order.tid)

        # Note. changing the order in the order_book list will also change the order in the orders dictonary
        
        # add the order to the orders dictionary
        n_orders = self.n_orders
        self.orders[order.tid] = order
        self.n_orders = len(self.orders)

        # add the order to order_book list
        position = self.find_order_book_position(order)
        self.order_book.insert(position, order)

        # return whether this was an addition or an overwrite
        if n_orders != self.n_orders :
            return('Addition')
        else:
            return('Overwrite')

    # delete the given order from the orders dictionary and from the order_book list
    def book_del(self, order):
                
        if self.orders.get(order.tid) != None :
            del(self.orders[order.tid])
            self.remove_from_order_book(order.tid)
            self.n_orders = len(self.orders)


# Orderbook for a single instrument: list of bids and list of asks

class Orderbook(Orderbook_half):

    def __init__(self):
        self.buy_side = Orderbook_half('Buy')
        self.sell_side = Orderbook_half('Sell')
        self.tape = []
        self.quote_id = 0  #unique ID code for each quote accepted onto the book



# Exchange's internal orderbook

class Exchange(Orderbook):

    def add_order(self, order, verbose):
        # add a quote/order to the exchange and update all internal records; return unique i.d.
        order.oid = self.quote_id
        self.quote_id = order.oid + 1
        # if verbose : print('QUID: order.quid=%d self.quote.id=%d' % (order.oid, self.quote_id))
        tid = order.tid
        if order.otype == 'Buy':
            response=self.buy_side.book_add(order)
        else:
            response=self.sell_side.book_add(order)
        return [order.oid, response]


    def del_order(self, time, order, verbose):
        # delete a trader's quot/order from the exchange, update all internal records
        tid = order.tid
        if order.otype == 'Buy':
            self.buy_side.book_del(order)
            cancel_record = { 'type': 'Cancel', 'time': time, 'order': order }
            self.tape.append(cancel_record)

        elif order.otype == 'Sell':
            self.sell_side.book_del(order)
            cancel_record = { 'type': 'Cancel', 'time': time, 'order': order }
            self.tape.append(cancel_record)
        else:
            # neither bid nor ask?
            sys.exit('bad order type in del_quote()')

    # match two orders and perform the trade
    # matching is buy-side friendly, so start with buys first
    def find_order_match(self):

        for buy_order in self.buy_side.order_book:
            for sell_order in self.sell_side.order_book:
                # find two matching orders in the order_book list
                if buy_order.qty >= sell_order.MES and buy_order.MES <= sell_order.qty:
                    # work out how large the trade size will be
                    if buy_order.qty >= sell_order.qty:
                        trade_size = sell_order.qty
                    else:
                        trade_size = buy_order.qty
                    # return a dictionary containing the trade info
                    # Note. Here we are returning references to the orders, so changing the returned orders will
                    # change the orders in the order_book
                    return {"buy_order": buy_order, "sell_order": sell_order, "trade_size": trade_size}

        # if no match can be found, return None
        return None

    # given a buy order, a sell order and a trade size, perform the trade
    def perform_trade(self, time, price, buy_order, sell_order, trade_size):

        # subtract the trade quantity from the orders' quantity
        buy_order.qty -= trade_size
        sell_order.qty -= trade_size

        # remove orders from the order_book
        self.buy_side.book_del(buy_order)
        self.sell_side.book_del(sell_order)

        # re-add the order to the order_book if there is still some quantity left over
        if buy_order.qty > 0:
            # update the MES if necessary
            if buy_order.MES > buy_order.qty:
                buy_order.MES = buy_order.qty
            # add the order to the order_book list
            self.buy_side.book_add(buy_order)

        # re-add the order to the order_book if there is still some quantity left over
        if sell_order.qty > 0:
            # update the MES if necessary
            if sell_order.MES > sell_order.qty:
                sell_order.MES = sell_order.qty
            # add the order to the order_book list
            self.sell_side.book_add(sell_order)

        # add a record of the transaction to the tape
        transaction_record = {  'type': 'Trade',
                                'time': time,
                                'price': price,
                                'party1': buy_order.tid,
                                'party2': sell_order.tid,
                                'qty': trade_size}
        self.tape.append(transaction_record)
        return transaction_record
        

    # this function executes the uncross event, trades occur at the given time at the given price
    # keep making trades out of matching order until no more matches can be found
    def uncross(self, time, price):

        # find a match between a buy order a sell order
        match_info = self.find_order_match()

        # keep on going until no more matches can be found
        while match_info != None:

            # execute the trade with the matched orders
            self.perform_trade(time, 50.0, match_info["buy_order"], match_info["sell_order"], match_info["trade_size"])

            # find another match
            match_info = self.find_order_match()

    def tape_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        for tapeitem in self.tape:
            if tapeitem['type'] == 'Trade' :
                dumpfile.write('%s, %s\n' % (tapeitem['time'], tapeitem['price']))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []


    # this returns the LOB data "published" by the exchange,
    # i.e., what is accessible to the traders
    def publish_lob(self, time, verbose):
        public_data = {}
        public_data['time'] = time
        public_data['OID'] = self.quote_id
        public_data['tape'] = self.tape
        return public_data

    # print the orders in the orders dictionary
    def print_orders(self):
        print("Buy orders:")
        for key in self.buy_side.orders:
            print(self.buy_side.orders[key])
        print("Sell orders:")
        for key in self.sell_side.orders:
            print(self.sell_side.orders[key])

    # print the orders in the order_book list
    def print_order_book(self):
        print("Buy side order book:")
        for order in self.buy_side.order_book:
            print(order)
        print("Sell side order book:")
        for order in self.sell_side.order_book:
            print(order)

##################--Traders below here--#############


# Trader superclass
# all Traders have a trader id, bank balance, blotter, and list of orders to execute
class Trader:

        def __init__(self, ttype, tid, balance, time):
                self.ttype = ttype      # what type / strategy this trader is
                self.tid = tid          # trader unique ID code
                self.balance = balance  # money in the bank
                self.blotter = []       # record of trades executed
                self.orders = []        # customer orders currently being worked (fixed at 1)
                self.n_quotes = 0       # number of quotes live on LOB
                self.willing = 1        # used in ZIP etc
                self.able = 1           # used in ZIP etc
                self.birthtime = time   # used when calculating age of a trader/strategy
                self.profitpertime = 0  # profit per unit time
                self.n_trades = 0       # how many trades has this trader done?
                self.lastquote = None   # record of what its last quote was


        def __str__(self):
                return '[TID %s type %s balance %s blotter %s orders %s n_trades %s profitpertime %s]' \
                       % (self.tid, self.ttype, self.balance, self.blotter, self.orders, self.n_trades, self.profitpertime)


        def add_order(self, order, verbose):
                # in this version, trader has at most one order,
                # if allow more than one, this needs to be self.orders.append(order)
                if self.n_quotes > 0 :
                    # this trader has a live quote on the LOB, from a previous customer order
                    # need response to signal cancellation/withdrawal of that quote
                    response = 'LOB_Cancel'
                else:
                    response = 'Proceed'
                self.orders = [order]
                if verbose : print('add_order < response=%s' % response)
                return response


        def del_order(self, order):
                # this is lazy: assumes each trader has only one customer order with quantity=1, so deleting sole order
                # CHANGE TO DELETE THE HEAD OF THE LIST AND KEEP THE TAIL
                self.orders = []


        def bookkeep(self, trade, order, verbose, time):

                outstr=""
                for order in self.orders: outstr = outstr + str(order)

                self.blotter.append(trade)  # add trade record to trader's blotter
                # NB What follows is **LAZY** -- assumes all orders are quantity=1
                transactionprice = trade['price']
                if self.orders[0].otype == 'Buy':
                        profit = self.orders[0].price - transactionprice
                else:
                        profit = transactionprice - self.orders[0].price
                self.balance += profit
                self.n_trades += 1
                self.profitpertime = self.balance/(time - self.birthtime)

                if profit < 0 :
                        print(profit)
                        print(trade)
                        print(order)
                        sys.exit()

                if verbose: print('%s profit=%d balance=%d profit/time=%d' % (outstr, profit, self.balance, self.profitpertime))
                self.del_order(order)  # delete the order


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

        def getorder(self, time, countdown, lob):
                if len(self.orders) < 1:
                        order = None
                else:
                        order = Order(self.tid,
                                    self.orders[0].otype,
                                    self.orders[0].qty,
                                    self.orders[0].MES,
                                    time)
                        self.lastquote=order
                return order



##########################---Below lies the experiment/test-rig---##################



# trade_stats()
# dump CSV statistics on exchange data and trader population to file for later analysis
# this makes no assumptions about the number of types of traders, or
# the number of traders of any one type -- allows either/both to change
# between successive calls, but that does make it inefficient as it has to
# re-analyse the entire set of traders on each call
def trade_stats(expid, traders, dumpfile, time, lob):
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
                        traders[t1name].tid = t2name
                        traders[t2name].tid = t1name
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
                                schedrange = sched['ranges']
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
                        quantity = random.randint(1,10)
                        MES = random.randint(1, quantity)
                        order = Order(tname, ordertype, quantity, MES, issuetime)
                        new_pending.append(order)
                        
                # add the supply side (sellers) customer orders to the list of pending orders
                issuetimes = getissuetimes(n_sellers, os['timemode'], os['interval'], shuffle_times, True)
                ordertype = 'Sell'
                (sched, mode) = getschedmode(time, os['sup'])
                for t in range(n_sellers):
                        issuetime = time + issuetimes[t]
                        tname = 'S%02d' % t
                        orderprice = getorderprice(t, sched, n_sellers, mode, issuetime)
                        # generating a random order quantity
                        quantity = random.randint(1,10)
                        MES = random.randint(1,quantity)
                        order = Order(tname, ordertype, quantity, MES, issuetime)
                        new_pending.append(order)
        # if there are some pending orders
        else:
                # there are pending future orders: issue any whose timestamp is in the past
                new_pending = []
                for order in pending:
                        if order.time < time:
                                # this order should have been issued by now
                                # issue it to the trader
                                tname = order.tid
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
                order = traders[tid].getorder(time, time_left, exchange.publish_lob(time, lob_verbose))

                if verbose: print('Trader Quote: %s' % (order))

                # if the randomly selected trader gives us a quote, then add it to the exchange
                if order != None:
                        # send order to exchange
                        traders[tid].n_quotes = 1
                        result = exchange.add_order(order, process_verbose)

                exchange.print_order_book()

                time = time + timestep


        # end of an experiment -- dump the tape
        exchange.tape_dump('transactions.csv', 'w', 'keep')


        # write trade_stats for this experiment NB end-of-session summary only
        trade_stats(sess_id, traders, dumpfile, time, exchange.publish_lob(time, lob_verbose))




def experiment1():

    start_time = 0.0
    end_time = 20.0
    duration = end_time - start_time

    range1 = (75, 125)
    supply_schedule = [ {'from':start_time, 'to':end_time, 'ranges':[range1], 'stepmode':'fixed'}
                      ]

    range1 = (75, 125)
    demand_schedule = [ {'from':start_time, 'to':end_time, 'ranges':[range1], 'stepmode':'fixed'}
                      ]

    order_sched = {'sup':supply_schedule, 'dem':demand_schedule,
                   'interval':10, 'timemode':'drip-fixed'}

    buyers_spec = [('GVWY',5)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec}

    n_trials = 1
    tdump=open('avg_balance.csv','w')
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


def test():

    # variables which dictate what information is printed to the output
    verbose = False
    traders_verbose = False
    orders_verbose = False
    lob_verbose = False
    process_verbose = False
    respond_verbose = False
    bookkeep_verbose = False

    # create the trader specs
    buyers_spec = [('GVWY',5)]
    sellers_spec = buyers_spec
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec}

    # initialise the exchange
    exchange = Exchange()

    # create a bunch of traders
    traders = {}
    trader_stats = populate_market(traders_spec, traders, True, traders_verbose)

    # create some orders
    orders = []
    orders.append(Order('B00', 'Buy', 5, 3, 25.0))
    orders.append(Order('B01', 'Buy', 10, 6, 35.0))
    orders.append(Order('B02', 'Buy', 3, 1, 55.0))
    orders.append(Order('B03', 'Buy', 3, 2, 75.0))
    orders.append(Order('B04', 'Buy', 3, 2, 65.0))
    orders.append(Order('S00', 'Sell', 11, 6, 45.0))
    orders.append(Order('S01', 'Sell', 4, 2, 55.0))
    orders.append(Order('S02', 'Sell', 6, 3, 65.0))
    orders.append(Order('S03', 'Sell', 6, 4, 55.0))
    
    # add the orders to the exchange
    for order in orders:
        exchange.add_order(order, orders_verbose)

    # print the order book before the uncross event
    print("\nStarting order book")
    exchange.print_order_book()

    # invoke an uncross event
    exchange.uncross(5.0, 25.0)

    # print the order book after the uncross event
    print("\nEnding order book")
    exchange.print_order_book()

    # print the tape at the end of the uncross event
    print("\ntape")
    print(exchange.tape)

    # end of an experiment -- dump the tape
    exchange.tape_dump('dark_transactions.csv', 'w', 'keep')

def main():
    test()

# the main function is called if BSE.py is run as the main program
if __name__ == "__main__":
    main()