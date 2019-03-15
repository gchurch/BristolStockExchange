import unittest
import dark_pool
import csv

###############################################################################
# Tests for the Order class

class Test_Order(unittest.TestCase):

    def test_init(self):

        # create an instance of the Order class
        tid = 'B5'
        otype = 'Bid'
        price = 100
        qty = 1
        time = 25.0
        qid = 10
        order = dark_pool.Order(tid, otype, price, qty, time, qid)

        # test all initialised member variables
        self.assertEqual(order.tid, tid)
        self.assertEqual(order.otype, otype)
        self.assertEqual(order.price, price)
        self.assertEqual(order.qty, qty)
        self.assertEqual(order.time, time)
        self.assertEqual(order.qid, qid)


#################################################################################
# tests for the Orderbook_half class

class Test_Orderbook_half(unittest.TestCase):

    def test_init(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # test all intialised member variables
        self.assertEqual(orderbook_half.booktype, booktype)
        self.assertEqual(orderbook_half.orders, {})
        self.assertEqual(orderbook_half.lob, {})
        self.assertEqual(orderbook_half.n_orders, 0)

    def test_build_lob(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the orders to the order book
        orderbook_half.book_add(order1)
        orderbook_half.book_add(order2)

        # build the lob
        orderbook_half.build_lob()

        # test that the lob is as expected
        self.assertEqual(orderbook_half.lob, {100: [1, [[25.0, 1, 'B1', 10]]], 150: [1, [[35.0, 1, 'B2', 20]]]})
        self.assertEqual(orderbook_half.best_price, 150)
        self.assertEqual(orderbook_half.best_tid, 'B2')

    def test_book_add(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the orders to the order book
        return_value1 = orderbook_half.book_add(order1)
        return_value2 = orderbook_half.book_add(order2)

        # test that the return values are as expected
        self.assertEqual(return_value1, 'Addition')
        self.assertEqual(return_value2, 'Addition')

        # test that the order books orders are as expected
        self.assertEqual(orderbook_half.orders, {'B1': order1, 'B2': order2})
        self.assertEqual(orderbook_half.n_orders, 2)


    def test_book_del(self):
        
        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the order to the order book and then delete it
        orderbook_half.book_add(order1)
        orderbook_half.book_add(order2)

        # delete order1
        orderbook_half.book_del(order1)

        # test that the orders are as expected
        self.assertEqual(orderbook_half.orders, {'B2': order2})
        self.assertEqual(orderbook_half.n_orders, 1)

        # delete order2
        orderbook_half.book_del(order2)

        # test that the orders are as expected
        self.assertEqual(orderbook_half.orders, {})
        self.assertEqual(orderbook_half.n_orders, 0)


################################################################################
# tests for the Orderbook class

class Test_Orderbook(unittest.TestCase):

    def test_init(self):

        orderbook = dark_pool.Orderbook()

        self.assertEqual(orderbook.tape, [])
        self.assertEqual(orderbook.quote_id, 0)
        self.assertEqual(orderbook.bids.lob, {})
        self.assertEqual(orderbook.asks.lob, {})

###############################################################################
# tests for Exchange class

class Test_Exchange(unittest.TestCase):

    def test_add_init(self):

        exchange = dark_pool.Exchange()

        self.assertEqual(exchange.tape, [])
        self.assertEqual(exchange.quote_id, 0)
        self.assertEqual(exchange.bids.lob, {})
        self.assertEqual(exchange.asks.lob, {})

    def test_add_order(self):
        
        # create an instance of the exchange class
        exchange = dark_pool.Exchange()

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = dark_pool.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = dark_pool.Order('S2', 'Ask', 190, 1, 55.0, 40)

        # add the orders to the exchange
        return_value1 = exchange.add_order(order1, False)
        return_value2 = exchange.add_order(order2, False)
        return_value3 = exchange.add_order(order3, False)
        return_value4 = exchange.add_order(order4, False)

        # test that the exchange's state is as expected
        self.assertEqual(exchange.bids.lob, {100: [1, [[25.0, 1, 'B1', 0]]], 150: [1, [[35.0, 1, 'B2', 1]]]})
        self.assertEqual(exchange.bids.best_price, 150)
        self.assertEqual(exchange.bids.best_tid, 'B2')
        self.assertEqual(exchange.asks.lob, {140: [1, [[45.0, 1, 'S1', 2]]], 190: [1, [[55.0, 1, 'S2', 3]]]})
        self.assertEqual(exchange.asks.best_price, 140)
        self.assertEqual(exchange.asks.best_tid, 'S1')

        # test the return values
        self.assertEqual(return_value1, [0, 'Addition'])
        self.assertEqual(return_value2, [1, 'Addition'])
        self.assertEqual(return_value3, [2, 'Addition'])
        self.assertEqual(return_value4, [3, 'Addition'])

    def test_del_order(self):

        # create an instance of the Exchange class
        exchange = dark_pool.Exchange()

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = dark_pool.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = dark_pool.Order('S2', 'Ask', 190, 1, 55.0, 40)

        # add the orders to the exchange
        exchange.add_order(order1, False)
        exchange.add_order(order2, False)
        exchange.add_order(order3, False)
        exchange.add_order(order4, False)

        # delete orders from the exchange
        exchange.del_order(100.0, order1, False)
        exchange.del_order(110.0, order4, False)

        # test that the exchange's state is as expected
        self.assertEqual(exchange.bids.lob, {150: [1, [[35.0, 1, 'B2', 1]]]})
        self.assertEqual(exchange.bids.best_price, 150)
        self.assertEqual(exchange.bids.best_tid, 'B2')
        self.assertEqual(exchange.asks.lob, {140: [1, [[45.0, 1, 'S1', 2]]]})
        self.assertEqual(exchange.asks.best_price, 140)
        self.assertEqual(exchange.asks.best_tid, 'S1')
        self.assertEqual(len(exchange.tape), 2)

class Test_Functions(unittest.TestCase):

    def test_populate_market(self):

        # create the trader specs
        buyers_spec = [('GVWY',2),('GVWY',1),('GVWY',2),('GVWY',3)]
        sellers_spec =[('GVWY',3),('GVWY',2),('GVWY',1),('GVWY',2)]
        traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec}

        # create an empty traders dict
        traders = {}

        # call the populate market function
        trader_stats = dark_pool.populate_market(traders_spec, traders, False, False)

        # test the results of the function call are as expected
        self.assertEqual(trader_stats, {'n_sellers': 8, 'n_buyers': 8})
        self.assertEqual(len(traders), 16)

#####################################################################################
# testing Trader class

class Test_Trader(unittest.TestCase):

    def test_init(self):

        # define argument values
    	ttype = 'GVWY'
        tid = 5
        balance = 0.5
        time = 5.0

        # create instance of the Trader class
        trader = dark_pool.Trader(ttype, tid, balance, time)

        # test that the initialisation performs as expected
        self.assertEqual(trader.ttype, ttype)
        self.assertEqual(trader.tid, tid)
        self.assertEqual(trader.balance, balance)
        self.assertEqual(trader.blotter, [])
        self.assertEqual(trader.orders, [])
        self.assertEqual(trader.n_quotes, 0)
        self.assertEqual(trader.willing, 1)
        self.assertEqual(trader.able, 1)
        self.assertEqual(trader.birthtime, time)
        self.assertEqual(trader.profitpertime, 0)
        self.assertEqual(trader.n_trades, 0)
        self.assertEqual(trader.lastquote, None)


    def test_add_order(self):

    	# create instance of the Trader class
        trader = dark_pool.Trader('GVWY', 5, 0.5, 5.0)

        # create instance of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)

        # call the add_order function
        response = trader.add_order(order1, False)

        # test the results are as expected
        self.assertEqual(len(trader.orders), 1)
        self.assertEqual(response, "Proceed")

    def test_del_order(self):
        
        # create trader
        trader = dark_pool.Trader('GVWY', 5, 0.5, 5.0)

        # create order
        order = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)

        # call the add_order function
        trader.add_order(order, False)

        # test that the length of the traders order member variable is 1
        self.assertEqual(len(trader.orders), 1)

        # call the del_order function
        trader.del_order(order)

        # test that the length of the traders order member variable is 0
        self.assertEqual(len(trader.orders), 0)


###########################################################################
# the code to be executed if this is the main program

if __name__ == "__main__":
    unittest.main()