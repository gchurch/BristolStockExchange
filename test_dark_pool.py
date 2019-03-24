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
        order = dark_pool.Order(tid, otype, qty, MES, time)

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
        self.assertEqual(orderbook_half.orders, {})
        self.assertEqual(orderbook_half.order_book, [])
        self.assertEqual(orderbook_half.n_orders, 0)

    # test that when a single order is added, it is added to the orders dictionary
    # and the order_book list
    def test__book_add__simple(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        # test
        self.assertEqual(orderbook_half.orders.keys(), ['B00'])
        self.assertEqual(orderbook_half.orders['B00'].__str__(), "Order [B00 Buy Q=5 MES=3 T=25.00 OID=-1]")
        self.assertEqual(orderbook_half.order_book[0].__str__(), "Order [B00 Buy Q=5 MES=3 T=25.00 OID=-1]")
        self.assertEqual(orderbook_half.n_orders, 1)

    # testing that when that the order of orders in the order_book list is ordered by quantity then time
    def test__book_add__ordering(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 4, 35.0))
        orders.append(dark_pool.Order('B02', 'Buy', 10, 4, 45.0))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        self.assertEqual(orderbook_half.orders.keys(), ['B01', 'B00', 'B02'])
        self.assertEqual(orderbook_half.orders['B00'].__str__(), "Order [B00 Buy Q=5 MES=3 T=25.00 OID=-1]")
        self.assertEqual(orderbook_half.orders['B01'].__str__(), "Order [B01 Buy Q=10 MES=4 T=35.00 OID=-1]")
        self.assertEqual(orderbook_half.orders['B02'].__str__(), "Order [B02 Buy Q=10 MES=4 T=45.00 OID=-1]")
        self.assertEqual(orderbook_half.order_book[0].__str__(), "Order [B01 Buy Q=10 MES=4 T=35.00 OID=-1]")
        self.assertEqual(orderbook_half.order_book[1].__str__(), "Order [B02 Buy Q=10 MES=4 T=45.00 OID=-1]")
        self.assertEqual(orderbook_half.order_book[2].__str__(), "Order [B00 Buy Q=5 MES=3 T=25.00 OID=-1]")

    def test__book_add__overwrite(self):
        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 4, 35.0))
        orders.append(dark_pool.Order('B00', 'Buy', 10, 4, 45.0))

        # add the orders and get the return values
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # tests
        self.assertEqual(return_values, ['Addition', 'Addition', 'Overwrite'])
        self.assertEqual(orderbook_half.orders.keys(), ['B01', 'B00'])
        self.assertEqual(orderbook_half.order_book[0].__str__(), "Order [B01 Buy Q=10 MES=4 T=35.00 OID=-1]")
        self.assertEqual(orderbook_half.order_book[1].__str__(), "Order [B00 Buy Q=10 MES=4 T=45.00 OID=-1]")
        self.assertEqual(orderbook_half.n_orders, 2)
        self.assertEqual(len(orderbook_half.order_book), 2)


    def test__book_del(self):
        
        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 4, 35.0))

        # add the orders
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # delete an order
        orderbook_half.book_del(orders[0])

        self.assertEqual(orderbook_half.n_orders, 1)



################################################################################
# tests for the Orderbook class

class Test_Orderbook(unittest.TestCase):

    def test__init__simple(self):

        orderbook = dark_pool.Orderbook()

        self.assertEqual(orderbook.tape, [])
        self.assertEqual(orderbook.quote_id, 0)
        self.assertEqual(orderbook.buy_side.orders, {})
        self.assertEqual(orderbook.sell_side.orders, {})
        self.assertEqual(orderbook.buy_side.order_book, [])
        self.assertEqual(orderbook.sell_side.order_book, [])

###############################################################################
# tests for Exchange class

class Test_Exchange(unittest.TestCase):

    def test__init__simple(self):

        exchange = dark_pool.Exchange()

        self.assertEqual(exchange.tape, [])
        self.assertEqual(exchange.quote_id, 0)
        self.assertEqual(exchange.buy_side.orders, {})
        self.assertEqual(exchange.sell_side.orders, {})

    def test__add_order(self):
        
        # create an exchange
        exchange = dark_pool.Exchange()

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 6, 35.0))
        orders.append(dark_pool.Order('B02', 'Buy', 3, 1, 55.0))
        orders.append(dark_pool.Order('B03', 'Buy', 3, 2, 75.0))
        orders.append(dark_pool.Order('B04', 'Buy', 3, 2, 65.0))
        orders.append(dark_pool.Order('S00', 'Sell', 11, 6, 45.0))
        orders.append(dark_pool.Order('S01', 'Sell', 4, 2, 55.0))
        orders.append(dark_pool.Order('S02', 'Sell', 6, 3, 65.0))
        orders.append(dark_pool.Order('S03', 'Sell', 6, 4, 55.0))

        # add the orders to the exchange
        return_values = []
        for order in orders:
            return_values.append(exchange.add_order(order, False))


    def test__del_order(self):

        # create an exchange
        exchange = dark_pool.Exchange()

        # create some orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 6, 35.0))
        orders.append(dark_pool.Order('B02', 'Buy', 3, 1, 55.0))
        orders.append(dark_pool.Order('B03', 'Buy', 3, 2, 75.0))
        orders.append(dark_pool.Order('B04', 'Buy', 3, 2, 65.0))
        orders.append(dark_pool.Order('S00', 'Sell', 11, 6, 45.0))
        orders.append(dark_pool.Order('S01', 'Sell', 4, 2, 55.0))
        orders.append(dark_pool.Order('S02', 'Sell', 6, 3, 65.0))
        orders.append(dark_pool.Order('S03', 'Sell', 6, 4, 55.0))

        # add the orders to the exchange
        for order in orders:
            exchange.add_order(order, False)

        # delete orders from the exchange
        exchange.del_order(100.0, orders[0], False)

        exchange.del_order(110.0, orders[-1], False)

    def test__uncross(self):
        # initialise the exchange
        exchange = dark_pool.Exchange()

        # create some example orders
        orders = []
        orders.append(dark_pool.Order('B00', 'Buy', 5, 3, 25.0))
        orders.append(dark_pool.Order('B01', 'Buy', 10, 6, 35.0))
        orders.append(dark_pool.Order('B02', 'Buy', 3, 1, 55.0))
        orders.append(dark_pool.Order('B03', 'Buy', 3, 2, 75.0))
        orders.append(dark_pool.Order('B04', 'Buy', 3, 2, 65.0))
        orders.append(dark_pool.Order('S00', 'Sell', 11, 6, 45.0))
        orders.append(dark_pool.Order('S01', 'Sell', 4, 2, 55.0))
        orders.append(dark_pool.Order('S02', 'Sell', 6, 3, 65.0))
        orders.append(dark_pool.Order('S03', 'Sell', 6, 4, 55.0))

        # add the orders to the exchange
        for order in orders:
            exchange.add_order(order, False)

        # invoke an uncross event, setting the traders parameters to None to avoid using traders
        exchange.uncross(None, 5.0, 25.0)

        # test the buy side
        self.assertEqual(len(exchange.buy_side.order_book), 0)

        # test the sell side
        self.assertEqual(len(exchange.sell_side.order_book), 3)
        self.assertEqual(exchange.sell_side.order_book[0].__str__(), "Order [S00 Sell Q=1 MES=1 T=45.00 OID=5]")
        self.assertEqual(exchange.sell_side.order_book[1].__str__(), "Order [S03 Sell Q=1 MES=1 T=55.00 OID=8]")
        self.assertEqual(exchange.sell_side.order_book[2].__str__(), "Order [S01 Sell Q=1 MES=1 T=55.00 OID=6]")

        # test the tape
        self.assertEqual(exchange.tape, [{'party2': 'S00', 'party1': 'B01', 'price': 50.0, 'time': 5.0, 'type': 'Trade', 'quantity': 10}, {'party2': 'S03', 'party1': 'B00', 'price': 50.0, 'time': 5.0, 'type': 'Trade', 'quantity': 5}, {'party2': 'S02', 'party1': 'B02', 'price': 50.0, 'time': 5.0, 'type': 'Trade', 'quantity': 3}, {'party2': 'S01', 'party1': 'B04', 'price': 50.0, 'time': 5.0, 'type': 'Trade', 'quantity': 3}, {'party2': 'S02', 'party1': 'B03', 'price': 50.0, 'time': 5.0, 'type': 'Trade', 'quantity': 3}])


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