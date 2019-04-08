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
        qty = 1
        MES = 1
        time = 25.0
        order = dark_pool.Order(time, tid, otype, qty, MES)

        # test all initialised member variables
        self.assertEqual(order.tid, tid)
        self.assertEqual(order.otype, otype)
        self.assertEqual(order.qty, qty)
        self.assertEqual(order.MES, MES)
        self.assertEqual(order.time, time)


#################################################################################
# tests for the Orderbook_half class

class Test_Orderbook_half(unittest.TestCase):

    # testing whether the initialised variables are as expected
    def test__init__simple(self):

        # create an instance of the Orderbook_half class
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # tests
        self.assertEqual(orderbook_half.booktype, booktype)
        self.assertEqual(orderbook_half.traders, {})
        self.assertEqual(orderbook_half.orders, [])
        self.assertEqual(orderbook_half.num_orders, 0)

    def test__find_order_position(self):
        
        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 4))
        orders.append(dark_pool.Order(45.0, 'B02', 'Buy', 10, 4))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        # test the positions are as expected
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 12, 4)), 0)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 10, 4)), 2)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 9, 4)), 2)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 4, 4)), 3)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(40.0, 'B03', 'Buy', 10, 4)), 1)

    def test__remove_from_order_book(self):
        return

    # test that when a single order is added, it is added to the orders dictionary
    # and the order_book list
    def test__book_add__simple(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        # test
        self.assertEqual(orderbook_half.traders.keys(), ['B00'])
        self.assertEqual(orderbook_half.traders['B00'], 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 MES=3]")
        self.assertEqual(orderbook_half.num_orders, 1)

    # testing that when that the order of orders in the order_book list is ordered by quantity then time
    def test__book_add__ordering(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 4))
        orders.append(dark_pool.Order(45.0, 'B02', 'Buy', 10, 4))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        self.assertEqual(orderbook_half.traders.keys(), ['B01', 'B00', 'B02'])
        self.assertEqual(orderbook_half.traders['B00'], 1)
        self.assertEqual(orderbook_half.traders['B01'], 1)
        self.assertEqual(orderbook_half.traders['B02'], 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B02 Buy Q=10 MES=4]")
        self.assertEqual(orderbook_half.orders[2].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 MES=3]")

    def test__book_add__overwrite(self):
        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 4))
        orders.append(dark_pool.Order(45.0, 'B00', 'Buy', 10, 4))

        # add the orders and get the return values
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # tests
        self.assertEqual(return_values, ['Addition', 'Addition', 'Overwrite'])
        self.assertEqual(orderbook_half.traders.keys(), ['B01', 'B00'])
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B00 Buy Q=10 MES=4]")
        self.assertEqual(orderbook_half.num_orders, 2)
        self.assertEqual(len(orderbook_half.orders), 2)


    def test__book_del(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 4))

        # add the orders
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # delete an order
        orderbook_half.book_del(orders[0].tid)

        self.assertEqual(orderbook_half.num_orders, 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 MES=4]")




##################################################################################################
# tests for the Orderbook class

class Test_Orderbook(unittest.TestCase):

    def test__init__simple(self):

        orderbook = dark_pool.Orderbook()

        self.assertEqual(orderbook.tape, [])
        self.assertEqual(orderbook.order_id, 0)
        self.assertEqual(orderbook.buy_side.traders, {})
        self.assertEqual(orderbook.sell_side.traders, {})
        self.assertEqual(orderbook.buy_side.orders, [])
        self.assertEqual(orderbook.sell_side.orders, [])

    def test__add_order__simple(self):

        # create the order book
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))

        # add the orders to the order book
        self.assertEqual(orderbook.add_order(orders[0], False), [0, 'Addition'])
        self.assertEqual(orderbook.add_order(orders[1], False), [1, 'Addition'])

        # check the state of the orderbook is as expected
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 MES=3]")
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 MES=6]")
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.num_orders, 1)
        self.assertEqual(orderbook.order_id, 2)

    def test__del_order(self):
        # create the order book
        orderbook = dark_pool.Orderbook()
 
        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))
        orders.append(dark_pool.Order(55.0, 'B01', 'Buy', 12, 3))

        # add the orders to the order book
        for order in orders:
            orderbook.add_order(order, False)

        # delete the first order
        orderbook.del_order(65.0, orders[0], False)

        # check that the state of the orderbook is as expected
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=2 T=55.00 B01 Buy Q=12 MES=3]")
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 MES=6]")
        self.assertEqual(orderbook.sell_side.num_orders, 1)


    def test__find_matching_orders(self):
        
        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))

        # add the orders to the orderbook
        for order in orders:
            orderbook.add_order(order, False)

        # attempt to find a match, none should be found
        self.assertEqual(orderbook.find_matching_orders(),None)

        # add add another order to the order book
        orderbook.add_order(dark_pool.Order(25.0, 'B01', 'Buy', 8, 7), False)

        # find a match
        match = orderbook.find_matching_orders()

        # test that the match is as expected
        self.assertEqual(match["trade_size"], 8)
        self.assertEqual(match["sell_order"].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 MES=6]")
        self.assertEqual(match["buy_order"].__str__(), "Order: [ID=2 T=25.00 B01 Buy Q=8 MES=7]")

    def test__perform_trade(self):
        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))

        # add the orders to the orderbook
        for order in orders:
            orderbook.add_order(order, False)

        # add add another order to the order book
        orderbook.add_order(dark_pool.Order(25.0, 'B01', 'Buy', 8, 7), False)

        # find a match
        match_info = orderbook.find_matching_orders()
        orderbook.perform_trade(None, 100.0, 50, match_info)

        self.assertEqual(orderbook.tape, [{'price': 50, 'seller': 'S00', 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 8}])
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 MES=3]")
        self.assertEqual(orderbook.sell_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=3 MES=3]")

###############################################################################
# tests for Exchange class

class Test_Exchange(unittest.TestCase):

    def test__init__simple(self):

        exchange = dark_pool.Exchange()

        self.assertEqual(exchange.order_book.tape, [])
        self.assertEqual(exchange.order_book.order_id, 0)
        self.assertEqual(exchange.order_book.buy_side.traders, {})
        self.assertEqual(exchange.order_book.sell_side.traders, {})

    def test__add_order__normal(self):
        
        # create an exchange
        exchange = dark_pool.Exchange()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))

        # add the orders to the exchange
        self.assertEqual(exchange.add_order(orders[0], False), [0, 'Addition'])
        self.assertEqual(exchange.add_order(orders[1], False), [1, 'Addition'])

        self.assertEqual(exchange.order_book.buy_side.num_orders, 1)
        self.assertEqual(exchange.order_book.sell_side.num_orders, 1)


    def test__del_order(self):

        # create an exchange
        exchange = dark_pool.Exchange()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))
        orders.append(dark_pool.Order(55.0, 'B01', 'Buy', 31, 3))

        # add the orders to the exchange
        return_values = []
        for order in orders:
            exchange.add_order(order, False)

        self.assertEqual(exchange.del_order(100.0, orders[0], False), None)
        self.assertEqual(exchange.order_book.buy_side.num_orders, 1)
        self.assertEqual(exchange.order_book.sell_side.num_orders, 1)

    def test__uncross(self):
        # initialise the exchange
        exchange = dark_pool.Exchange()

        # create some example orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 6))
        orders.append(dark_pool.Order(55.0, 'B02', 'Buy', 3, 1))
        orders.append(dark_pool.Order(75.0, 'B03', 'Buy', 3, 2))
        orders.append(dark_pool.Order(65.0, 'B04', 'Buy', 3, 2))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 6))
        orders.append(dark_pool.Order(55.0, 'S01', 'Sell', 4, 2))
        orders.append(dark_pool.Order(65.0, 'S02', 'Sell', 6, 3))
        orders.append(dark_pool.Order(55.0, 'S03', 'Sell', 6, 4))

        # add the orders to the exchange
        for order in orders:
            exchange.add_order(order, False)

        # invoke an uncross event, setting the traders parameters to None to avID using traders
        exchange.uncross(None, 5.0, 25.0)

        # test the buy side
        self.assertEqual(len(exchange.order_book.buy_side.orders), 0)

        # test the sell side
        self.assertEqual(len(exchange.order_book.sell_side.orders), 3)
        self.assertEqual(exchange.order_book.sell_side.orders[0].__str__(), "Order: [ID=5 T=45.00 S00 Sell Q=1 MES=1]")
        self.assertEqual(exchange.order_book.sell_side.orders[1].__str__(), "Order: [ID=8 T=55.00 S03 Sell Q=1 MES=1]")
        self.assertEqual(exchange.order_book.sell_side.orders[2].__str__(), "Order: [ID=6 T=55.00 S01 Sell Q=1 MES=1]")

        # test the tape
        self.assertEqual(exchange.order_book.tape, [{'price': 50.0, 'seller': 'S00', 'time': 5.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 10}, {'price': 50.0, 'seller': 'S03', 'time': 5.0, 'buyer': 'B00', 'type': 'Trade', 'quantity': 5}, {'price': 50.0, 'seller': 'S02', 'time': 5.0, 'buyer': 'B02', 'type': 'Trade', 'quantity': 3}, {'price': 50.0, 'seller': 'S01', 'time': 5.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 3}, {'price': 50.0, 'seller': 'S02', 'time': 5.0, 'buyer': 'B03', 'type': 'Trade', 'quantity': 3}])

        def test__tape_dump(self):
            return

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

#class Test_Trader(unittest.TestCase):
#
#    def test_init(self):

#        # define argument values
#    	ttype = 'GVWY'
#        tid = 5
#        balance = 0.5
#        time = 5.0

#        # create instance of the Trader class
#        trader = dark_pool.Trader(ttype, tid, balance, time)

#        # test that the initialisation performs as expected
#        self.assertEqual(trader.ttype, ttype)
#        self.assertEqual(trader.tid, tid)
#        self.assertEqual(trader.balance, balance)
#        self.assertEqual(trader.blotter, [])
#        self.assertEqual(trader.orders, [])
#        self.assertEqual(trader.n_quotes, 0)
#        self.assertEqual(trader.willing, 1)
#        self.assertEqual(trader.able, 1)
#        self.assertEqual(trader.birthtime, time)
#        self.assertEqual(trader.profitpertime, 0)
#        self.assertEqual(trader.n_trades, 0)
#        self.assertEqual(trader.lastquote, None)


#    def test_add_order(self):

#    	# create instance of the Trader class
#        trader = dark_pool.Trader('GVWY', 5, 0.5, 5.0)

#        # create instance of the Order class
#        order1 = dark_pool.Order('B1', 'Bid', 1, 25.0, 10)

#        # call the add_order function
#        response = trader.add_order(order1, False)

#        # test the results are as expected
#        self.assertEqual(len(trader.orders), 1)
#        self.assertEqual(response, "Proceed")

#    def test_del_order(self):
        
#        # create trader
#        trader = dark_pool.Trader('GVWY', 5, 0.5, 5.0)

#        # create order
#        order = dark_pool.Order('B1', 'Bid', 1, 25.0, 10)

#        # call the add_order function
#        trader.add_order(order, False)

#        # test that the length of the traders order member variable is 1
#        self.assertEqual(len(trader.orders), 1)

#        # call the del_order function
#        trader.del_order(order)

#        # test that the length of the traders order member variable is 0
#        self.assertEqual(len(trader.orders), 0)


###########################################################################
# the code to be executed if this is the main program

if __name__ == "__main__":
    unittest.main()