import unittest
import dark_pool
import csv

###############################################################################
# Tests for the Order class

class Test_Order(unittest.TestCase):

    # test the __init__ function
    def test__init__(self):

        # create an Order
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        MES = 1
        limit_price = 0
        time = 25.0
        order = dark_pool.Order(time, tid, otype, qty, limit_price, MES)

        # test all initialised member variables
        self.assertEqual(order.trader_id, tid)
        self.assertEqual(order.otype, otype)
        self.assertEqual(order.quantity, qty)
        self.assertEqual(order.limit_price, limit_price)
        self.assertEqual(order.MES, MES)
        self.assertEqual(order.time, time)

    # test the __str__ function
    def test__str__(self):

        # create an Order
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        MES = 1
        time = 25.0
        limit_price = 1
        order = dark_pool.Order(time, tid, otype, qty, limit_price, MES)

        # test that the string produced is as expected
        self.assertEqual(order.__str__(), "Order: [ID=-1 T=25.00 B5 Bid Q=1 P=1 MES=1]")

#################################################################################
# tests for the Block_Indication class

class Test_Block_Indication(unittest.TestCase):

    # test the __init__ function
    def test__init__(self):

        # create a Block Indication
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        BI = dark_pool.Block_Indication(time, tid, otype, qty, limit_price, MES)

        # test all initialised member variables
        self.assertEqual(BI.trader_id, tid)
        self.assertEqual(BI.otype, otype)
        self.assertEqual(BI.quantity, qty)
        self.assertEqual(BI.limit_price, limit_price)
        self.assertEqual(BI.MES, MES)
        self.assertEqual(BI.time, time)

    # test the __str__ function
    def test__str__(self):

        # create a Block Indication
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        BI = dark_pool.Block_Indication(time, tid, otype, qty, limit_price, MES)   

        # test that the string is as expected
        self.assertEqual(BI.__str__(), "BI: [ID=-1 T=25.00 B5 Bid Q=1 P=100 MES=1]")

#################################################################################
# tests for the Order_Submission_Request class

class Test_Order_Submission_Request(unittest.TestCase):

    # test the __init__ function
    def test__init__(self):

        # create an Order Submission Request
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        OSR = dark_pool.Order_Submission_Request(time, tid, otype, qty, limit_price, MES, match_id)

        # test that the intialized values are as expected
        self.assertEqual(OSR.time, time)
        self.assertEqual(OSR.trader_id, tid)
        self.assertEqual(OSR.otype, otype)
        self.assertEqual(OSR.quantity, qty)
        self.assertEqual(OSR.limit_price, limit_price)
        self.assertEqual(OSR.MES, MES)
        self.assertEqual(OSR.match_id, match_id)

    # test the __str__ function
    def test__str__(self):

        # create a Order Submission Request
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        OSR = dark_pool.Order_Submission_Request(time, tid, otype, qty, limit_price, MES, match_id)

        # test that the string is as expected
        self.assertEqual(OSR.__str__(), "OSR: [ID=-1 T=25.00 B5 Bid Q=1 P=100 MES=1 MID=0]")


#################################################################################
# tests for the Qualifying_Block_Order class

class Test_Qualifying_Block_Order(unittest.TestCase):

    # test the __init__ function
    def test__init__(self):

        # create a qualifying block order
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        QBO = dark_pool.Qualifying_Block_Order(time, tid, otype, qty, limit_price, MES, match_id)

        # test that the initialized values are as expected
        self.assertEqual(QBO.time, time)
        self.assertEqual(QBO.trader_id, tid)
        self.assertEqual(QBO.otype, otype)
        self.assertEqual(QBO.quantity, qty)
        self.assertEqual(QBO.limit_price, limit_price)
        self.assertEqual(QBO.MES, MES)
        self.assertEqual(QBO.match_id, match_id)

    # test the __str__ function
    def test__str__(self):

        # create a qualifying block order
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        QBO = dark_pool.Qualifying_Block_Order(time, tid, otype, qty, limit_price, MES, match_id)

        # test that the string is as expected
        self.assertEqual(QBO.__str__(), "QBO: [ID=-1 T=25.00 B5 Bid Q=1 P=100 MES=1 MID=0]")


#################################################################################
# tests for the Orderbook_half class

class Test_Orderbook_half(unittest.TestCase):

    # testing whether the initialised variables are as expected
    def test__init__(self):

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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 120, 4))
        orders.append(dark_pool.Order(45.0, 'B02', 'Buy', 10, 90, 4))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        # test the positions are as expected
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 12, None, 4)), 0)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 10, None, 4)), 2)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 9, None, 4)), 2)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(55.0, 'B03', 'Buy', 4, None, 4)), 3)
        self.assertEqual(orderbook_half.find_order_position(dark_pool.Order(40.0, 'B03', 'Buy', 10, None, 4)), 1)

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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        # test
        self.assertEqual(orderbook_half.traders.keys(), ['B00'])
        self.assertEqual(orderbook_half.traders['B00'], 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 P=100 MES=3]")
        self.assertEqual(orderbook_half.num_orders, 1)

    # testing that when that the order of orders in the order_book list is ordered by quantity then time
    def test__book_add__ordering(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 100, 4))
        orders.append(dark_pool.Order(45.0, 'B02', 'Buy', 10, 110, 4))

        # add the orders
        for order in orders:
            orderbook_half.book_add(order)

        self.assertEqual(orderbook_half.traders.keys(), ['B01', 'B00', 'B02'])
        self.assertEqual(orderbook_half.traders['B00'], 1)
        self.assertEqual(orderbook_half.traders['B01'], 1)
        self.assertEqual(orderbook_half.traders['B02'], 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 P=100 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B02 Buy Q=10 P=110 MES=4]")
        self.assertEqual(orderbook_half.orders[2].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 P=100 MES=3]")

    def test__book_add__overwrite(self):
        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 121, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 221, 4))
        orders.append(dark_pool.Order(45.0, 'B00', 'Buy', 10, 112, 4))

        # add the orders and get the return values
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # tests
        self.assertEqual(return_values, ['Addition', 'Addition', 'Overwrite'])
        self.assertEqual(orderbook_half.traders.keys(), ['B01', 'B00'])
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 P=221 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B00 Buy Q=10 P=112 MES=4]")
        self.assertEqual(orderbook_half.num_orders, 2)
        self.assertEqual(len(orderbook_half.orders), 2)


    def test__book_del(self):

        # create the order book
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 121, 3))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 111, 4))

        # add the orders
        return_values = []
        for order in orders:
            return_values.append(orderbook_half.book_add(order))

        # delete an order
        orderbook_half.book_del(orders[0].trader_id)

        self.assertEqual(orderbook_half.num_orders, 1)
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 P=111 MES=4]")




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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 100, 6))

        # add the orders to the order book
        self.assertEqual(orderbook.add_order(orders[0], False), [0, 'Addition'])
        self.assertEqual(orderbook.add_order(orders[1], False), [1, 'Addition'])

        # check the state of the orderbook is as expected
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 P=100 MES=3]")
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 P=100 MES=6]")
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.num_orders, 1)
        self.assertEqual(orderbook.order_id, 2)

    def test__del_order(self):
        # create the order book
        orderbook = dark_pool.Orderbook()
 
        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 100, 6))
        orders.append(dark_pool.Order(55.0, 'B01', 'Buy', 12, 100, 3))

        # add the orders to the order book
        for order in orders:
            orderbook.add_order(order, False)

        # delete the first order
        orderbook.del_order(65.0, orders[0], False)

        # check that the state of the orderbook is as expected
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=2 T=55.00 B01 Buy Q=12 P=100 MES=3]")
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 P=100 MES=6]")
        self.assertEqual(orderbook.sell_side.num_orders, 1)


    def test__find_matching_orders(self):
        
        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 49, 6))

        # add the orders to the orderbook
        for order in orders:
            orderbook.add_order(order, False)

        # attempt to find a match, none should be found
        self.assertEqual(orderbook.find_matching_orders(50), None)

        # add add another order to the order book
        orderbook.add_order(dark_pool.Order(25.0, 'B01', 'Buy', 8, 53, 7), False)

        # find a match
        match = orderbook.find_matching_orders(50)

        # test that the match is as expected
        self.assertEqual(match["trade_size"], 8)
        self.assertEqual(match["sell_order"].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 P=49 MES=6]")
        self.assertEqual(match["buy_order"].__str__(), "Order: [ID=2 T=25.00 B01 Buy Q=8 P=53 MES=7]")

    def test__perform_trade(self):
        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6))

        # add the orders to the orderbook
        for order in orders:
            orderbook.add_order(order, False)

        # add add another order to the order book
        orderbook.add_order(dark_pool.Order(25.0, 'B01', 'Buy', 8, 55, 7), False)

        # find a match
        match_info = orderbook.find_matching_orders(50)
        orderbook.perform_trade(None, 100.0, 50, match_info)

        self.assertEqual(orderbook.tape, [{'price': 50, 'seller': 'S00', 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 8}])
        self.assertEqual(orderbook.buy_side.num_orders, 1)
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 P=56 MES=3]")
        self.assertEqual(orderbook.sell_side.num_orders, 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=3 P=46 MES=3]")

###############################################################################
# tests for the Block_Indication_Book class

class Test_Block_Indication_Book(unittest.TestCase):

    def test__init__(self):

        block_indication_book = dark_pool.Block_Indication_Book()

        self.assertEqual(block_indication_book.BI_id, 0)
        self.assertEqual(block_indication_book.reputational_scores, {})
        self.assertEqual(block_indication_book.matches, {})
        self.assertEqual(block_indication_book.QBO_id, 0)
        self.assertEqual(block_indication_book.match_id, 0)
        self.assertEqual(block_indication_book.tape, [])
        self.assertEqual(block_indication_book.OSR_id, 0)

    def test__add_block_indication(self):

        # create a block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))

        # add the block indications
        self.assertEqual(block_indication_book.add_block_indication(block_indications[0], False), [0, 'Addition'])
        self.assertEqual(block_indication_book.add_block_indication(block_indications[1], False), [1, 'Addition'])

        # check that the block indications were added correctly
        self.assertEqual(block_indication_book.buy_side.orders[0].__str__(), "BI: [ID=0 T=100.00 B00 Buy Q=1024 P=125 MES=500]")
        self.assertEqual(block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=1 T=100.00 S00 Sell Q=999 P=1 MES=1]")

        # check that reputational scores are correctly assigned
        self.assertEqual(block_indication_book.reputational_scores['B00'], block_indication_book.initial_reputational_scores_value)
        self.assertEqual(block_indication_book.reputational_scores['S00'], block_indication_book.initial_reputational_scores_value)

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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6))

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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6))
        orders.append(dark_pool.Order(55.0, 'B01', 'Buy', 31, None, 3))

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
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, None))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 50, 6))
        orders.append(dark_pool.Order(55.0, 'B02', 'Buy', 3, 53, 1))
        orders.append(dark_pool.Order(75.0, 'B03', 'Buy', 3, 59, 2))
        orders.append(dark_pool.Order(65.0, 'B04', 'Buy', 3, 61, 2))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 51, 6))
        orders.append(dark_pool.Order(55.0, 'S01', 'Sell', 4, 43, 2))
        orders.append(dark_pool.Order(65.0, 'S02', 'Sell', 6, 48, 3))
        orders.append(dark_pool.Order(55.0, 'S03', 'Sell', 6, 49, 4))

        # add the orders to the exchange
        for order in orders:
            exchange.add_order(order, False)

        # invoke an uncross event, setting the traders parameters to None to avID using traders
        exchange.uncross(None, 100.0, 50.0)

        # test the buy side
        self.assertEqual(len(exchange.order_book.buy_side.orders), 3)

        # test the sell side
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=4 T=65.00 B04 Buy Q=3 P=61 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[1].__str__(), "Order: [ID=3 T=75.00 B03 Buy Q=3 P=59 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[2].__str__(), "Order: [ID=2 T=55.00 B02 Buy Q=2 P=53 MES=1]")

        # test the tape
        self.assertEqual(exchange.order_book.tape, [{'price': 50, 'seller': 'S03', 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 6}, {'price': 50, 'seller': 'S02', 'time': 100.0, 'buyer': 'B00', 'type': 'Trade', 'quantity': 5}, {'price': 50, 'seller': 'S01', 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 4}, {'price': 50, 'seller': 'S02', 'time': 100.0, 'buyer': 'B02', 'type': 'Trade', 'quantity': 1}])

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
#        self.assertEqual(trader.trader_id, tid)
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