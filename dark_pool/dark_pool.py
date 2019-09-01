from orders import *
from orderbook_half import *
from orderbook import *
from block_indication_book import *
from exchange import *;
from trader import *;

import sys
import math
import random
import copy

bse_sys_minprice = 1  # minimum price in the system, in cents/pennies
bse_sys_maxprice = 1000  # maximum price in the system, in cents/pennies
ticksize = 1  # minimum change in price, in cents/pennies


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
                        return Trader_BDS_Giveaway('GVWY', name, 0.00, 0)
                elif robottype == 'GVWY_test':
                        return Trader_BDS_Giveaway_test('GVWY', name, 0.00, 0)
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
    exchange.block_indication_book.MIV = 800


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
    exchange.tape_dump('output/transactions.csv', 'w', 'keep')
    # dump the traders' reputational score history
    exchange.CRS_history_dump('output/CRS_history.csv', 'w', 'keep')
    exchange.ERS_dump('output/ERS.csv', 'w', 'keep')

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
    traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec, 'BI_threshold':800}

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