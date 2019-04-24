import unittest
import dark_pool
import csv

###############################################################################
# Tests for the Order class

class Test_Order(unittest.TestCase):

    # test the __init__ function
    def test_init_function(self):

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
        self.assertEqual(order.quantity_remaining, qty)

    # test the __str__ function
    def test_str_function(self):

        # create an Order
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        MES = 1
        time = 25.0
        limit_price = 1
        order = dark_pool.Order(time, tid, otype, qty, limit_price, MES)

        # test that the string produced is as expected
        self.assertEqual(order.__str__(), "Order: [ID=-1 T=25.00 B5 Bid Q=1 QR=1 P=1 MES=1]")

#################################################################################
# tests for the Block_Indication class

class Test_Block_Indication(unittest.TestCase):

    # test the __init__ function
    def test_init_function(self):

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
    def test_str_function(self):

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
    def test_init_function(self):

        # create an Order Submission Request
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        CRP = 80
        OSR = dark_pool.Order_Submission_Request(time, tid, otype, qty, limit_price, MES, match_id, CRP)

        # test that the intialized values are as expected
        self.assertEqual(OSR.time, time)
        self.assertEqual(OSR.trader_id, tid)
        self.assertEqual(OSR.otype, otype)
        self.assertEqual(OSR.quantity, qty)
        self.assertEqual(OSR.limit_price, limit_price)
        self.assertEqual(OSR.MES, MES)
        self.assertEqual(OSR.match_id, match_id)
        self.assertEqual(OSR.reputational_score, CRP)

    # test the __str__ function
    def test_str_function(self):

        # create a Order Submission Request
        time = 25.0
        tid = 'B5'
        otype = 'Bid'
        qty = 1
        limit_price = 100
        MES = 1
        match_id = 0
        CRP = 80
        OSR = dark_pool.Order_Submission_Request(time, tid, otype, qty, limit_price, MES, match_id, CRP)

        # test that the string is as expected
        self.assertEqual(OSR.__str__(), "OSR: [ID=-1 T=25.00 B5 Bid Q=1 P=100 MES=1 MID=0 CRP=80]")


#################################################################################
# tests for the Qualifying_Block_Order class

class Test_Qualifying_Block_Order(unittest.TestCase):

    # test the __init__ function
    def test_init_function(self):

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
    def test_str_function(self):

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
    def test_init_function(self):

        # create an instance of the Orderbook_half class
        booktype = "Buy"
        orderbook_half = dark_pool.Orderbook_half(booktype)

        # tests
        self.assertEqual(orderbook_half.booktype, booktype)
        self.assertEqual(orderbook_half.traders, {})
        self.assertEqual(orderbook_half.orders, [])

    def test_find_order_position_function(self):
        
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

    # test that when a single order is added, it is added to the orders dictionary
    # and the order_book list
    def test_book_add_function_simple(self):

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
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 QR=5 P=100 MES=3]")

    # testing that when that the order of orders in the order_book list is ordered by quantity then time
    def test_book_add_function_ordering(self):

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
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 QR=10 P=100 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B02 Buy Q=10 QR=10 P=110 MES=4]")
        self.assertEqual(orderbook_half.orders[2].__str__(), "Order: [ID=-1 T=25.00 B00 Buy Q=5 QR=5 P=100 MES=3]")

    def test_book_add_function_overwrite(self):
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
        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 QR=10 P=221 MES=4]")
        self.assertEqual(orderbook_half.orders[1].__str__(), "Order: [ID=-1 T=45.00 B00 Buy Q=10 QR=10 P=112 MES=4]")
        self.assertEqual(len(orderbook_half.orders), 2)


    def test_book_del_function(self):

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

        self.assertEqual(orderbook_half.orders[0].__str__(), "Order: [ID=-1 T=35.00 B01 Buy Q=10 QR=10 P=111 MES=4]")


    def test_trader_has_order_function(self):

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

        self.assertTrue(orderbook_half.trader_has_order('B00'))
        self.assertTrue(orderbook_half.trader_has_order('B01'))
        self.assertTrue(orderbook_half.trader_has_order('B02'))
        self.assertFalse(orderbook_half.trader_has_order('B03'))
        self.assertFalse(orderbook_half.trader_has_order('B04'))

##################################################################################################
# tests for the Orderbook class

class Test_Orderbook(unittest.TestCase):

    def test_init_function(self):

        orderbook = dark_pool.Orderbook()

        self.assertEqual(orderbook.tape, [])
        self.assertEqual(orderbook.order_id, 0)
        self.assertEqual(orderbook.buy_side.traders, {})
        self.assertEqual(orderbook.sell_side.traders, {})
        self.assertEqual(orderbook.buy_side.orders, [])
        self.assertEqual(orderbook.sell_side.orders, [])

    def test_add_order_function_simple(self):

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
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 QR=5 P=100 MES=3]")
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=11 P=100 MES=6]")
        self.assertEqual(len(orderbook.buy_side.orders), 1)
        self.assertEqual(len(orderbook.sell_side.orders), 1)
        self.assertEqual(orderbook.order_id, 2)

    def test_add_order_function_overwrite(self):
        # create the order book
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 100, 6))
        orders.append(dark_pool.Order(35.0, 'B00', 'Buy', 15, 110, 3))

        return_values = []

        for order in orders:
            return_values.append(orderbook.add_order(order, False))

        self.assertEqual(return_values, [[0, 'Addition'], [1, 'Addition'], [2, 'Overwrite']])
        self.assertEqual(len(orderbook.buy_side.orders), 1)
        self.assertEqual(len(orderbook.sell_side.orders), 1)
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=2 T=35.00 B00 Buy Q=15 QR=15 P=110 MES=3]")
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=11 P=100 MES=6]")

    def test_add_order_function_overwrite_across_sides(self):
        # create the order book
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 100, 6))
        orders.append(dark_pool.Order(35.0, 'B00', 'Sell', 15, 110, 3))

        return_values = []

        for order in orders:
            return_values.append(orderbook.add_order(order, False))

        self.assertEqual(return_values, [[0, 'Addition'], [1, 'Addition'], [2, 'Overwrite']])
        self.assertEqual(len(orderbook.buy_side.orders), 0)
        self.assertEqual(len(orderbook.sell_side.orders), 2)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=2 T=35.00 B00 Sell Q=15 QR=15 P=110 MES=3]")
        self.assertEqual(orderbook.sell_side.orders[1].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=11 P=100 MES=6]")

    def test_add_order_function_overwrite_across_books(self):
        return

    def test_trader_has_order_function(self):
        
        # create the order book
        orderbook = dark_pool.Orderbook()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, 100, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 100, 6))

        for order in orders:
            orderbook.add_order(order, False)

        self.assertTrue(orderbook.trader_has_order('B00'))
        self.assertTrue(orderbook.trader_has_order('S00'))
        self.assertFalse(orderbook.trader_has_order('B01'))
        self.assertFalse(orderbook.trader_has_order('S01'))


    def test_del_order_function(self):
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
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=2 T=55.00 B01 Buy Q=12 QR=12 P=100 MES=3]")
        self.assertEqual(len(orderbook.buy_side.orders), 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=11 P=100 MES=6]")
        self.assertEqual(len(orderbook.sell_side.orders), 1)


    def test_check_price_match_function(self):
        
        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(orderbook.check_price_match(order1, order2, 50))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(orderbook.check_price_match(order1, order2, 50))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6)
        self.assertTrue(orderbook.check_price_match(order1, order2, 50))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6)
        self.assertTrue(orderbook.check_price_match(order1, order2, 50))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 51, 6)
        self.assertFalse(orderbook.check_price_match(order1, order2, 50))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 49, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(orderbook.check_price_match(order1, order2, 50))

    def test_check_size_match_function(self):

        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders and test them

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, None)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 11, 56, None)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        order2 = dark_pool.Order(25.0, 'B00', 'Buy', 5, 56, 3)
        self.assertFalse(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        order2 = dark_pool.Order(25.0, 'B00', 'Buy', 7, 56, 3)
        self.assertTrue(orderbook.check_size_match(order1, order2))

        order1 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        order2 = dark_pool.Order(25.0, 'B00', 'Buy', 7, 56, 3)
        order2.quantity_remaining = 5
        self.assertFalse(orderbook.check_size_match(order1, order2))

    def test_check_match_function(self):

        # create the orderbook
        orderbook = dark_pool.Orderbook()

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 56, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 50, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 50, 6)
        self.assertTrue(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 50, 3)
        order1.quantity_remaining = 5
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 50, 6)
        self.assertFalse(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 49, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 51, 6)
        self.assertFalse(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, None, 3)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 11, None, None)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, None, None)
        self.assertTrue(orderbook.check_match(order1, order2, 50))

        # create some orders
        order1 = dark_pool.Order(25.0, 'B00', 'Buy', 6, 49, None)
        order2 = dark_pool.Order(45.0, 'S00', 'Sell', 11, None, None)
        self.assertFalse(orderbook.check_match(order1, order2, 50))


    def test_find_matching_orders_function(self):
        
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
        self.assertEqual(match["sell_order"].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=11 P=49 MES=6]")
        self.assertEqual(match["buy_order"].__str__(), "Order: [ID=2 T=25.00 B01 Buy Q=8 QR=8 P=53 MES=7]")

    def test_execute_trade_function(self):
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
        orderbook.execute_trade(100.0, match_info)

        self.assertEqual(orderbook.tape, [{'price': 50, 'seller': 'S00', 'BDS': False, 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 8}])
        self.assertEqual(len(orderbook.buy_side.orders), 1)
        self.assertEqual(orderbook.buy_side.orders[0].__str__(), "Order: [ID=0 T=25.00 B00 Buy Q=5 QR=5 P=56 MES=3]")
        self.assertEqual(len(orderbook.sell_side.orders), 1)
        self.assertEqual(orderbook.sell_side.orders[0].__str__(), "Order: [ID=1 T=45.00 S00 Sell Q=11 QR=3 P=46 MES=3]")


    def test_execute_trades_function(self):
        # initialise the exchange
        exchange = dark_pool.Exchange()

        # create some example orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, None))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, 50, 6))
        orders.append(dark_pool.Order(55.0, 'B02', 'Buy', 3, 53, 1))
        orders.append(dark_pool.Order(75.0, 'B03', 'Buy', 3, 59, 2))
        orders.append(dark_pool.Order(65.0, 'B04', 'Buy', 3, 61, 2))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, 49, 6))
        orders.append(dark_pool.Order(55.0, 'S01', 'Sell', 4, 43, 2))
        orders.append(dark_pool.Order(65.0, 'S02', 'Sell', 6, 48, 3))
        orders.append(dark_pool.Order(55.0, 'S03', 'Sell', 6, 49, 4))

        # add the orders to the exchange
        for order in orders:
            exchange.add_order(order, False)

        # invoke an uncross event, setting the traders parameters to None to avID using traders
        exchange.execute_trades(100.0, 50.0)

        # test the buy side
        self.assertEqual(len(exchange.order_book.buy_side.orders), 1)
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=2 T=55.00 B02 Buy Q=3 QR=1 P=53 MES=1]")

        # test the sell side
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)
        self.assertEqual(exchange.order_book.sell_side.orders[0].__str__(), "Order: [ID=6 T=55.00 S01 Sell Q=4 QR=4 P=43 MES=2]")

        # test the tape
        self.assertEqual(exchange.order_book.tape, [{'price': 50.0, 'seller': 'S00', 'BDS': False, 'time': 100.0, 'buyer': 'B01', 'type': 'Trade', 'quantity': 10}, {'price': 50.0, 'seller': 'S00', 'BDS': False, 'time': 100.0, 'buyer': 'B00', 'type': 'Trade', 'quantity': 1}, {'price': 50.0, 'seller': 'S03', 'BDS': False, 'time': 100.0, 'buyer': 'B00', 'type': 'Trade', 'quantity': 4}, {'price': 50.0, 'seller': 'S03', 'BDS': False, 'time': 100.0, 'buyer': 'B02', 'type': 'Trade', 'quantity': 2}, {'price': 50.0, 'seller': 'S02', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 3}, {'price': 50.0, 'seller': 'S02', 'BDS': False, 'time': 100.0, 'buyer': 'B03', 'type': 'Trade', 'quantity': 3}])

###############################################################################
# tests for the Block_Indication_Book class

class Test_Block_Indication_Book(unittest.TestCase):

    def test_init_function(self):

        block_indication_book = dark_pool.Block_Indication_Book()

        self.assertEqual(block_indication_book.BI_id, 0)
        self.assertEqual(block_indication_book.QBO_id, 0)
        self.assertEqual(block_indication_book.OSR_id, 0)
        self.assertEqual(block_indication_book.composite_reputational_scores, {})
        self.assertEqual(block_indication_book.event_reputational_scores, {})
        self.assertEqual(block_indication_book.matches, {})
        self.assertEqual(block_indication_book.match_id, 0)
        self.assertEqual(block_indication_book.tape, [])

    def test_add_block_indication_function(self):

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
        self.assertEqual(block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=1 T=100.00 S00 Sell Q=999 P=None MES=None]")

        # check that reputational scores are correctly assigned
        self.assertEqual(block_indication_book.composite_reputational_scores['B00'], block_indication_book.initial_composite_reputational_score)
        self.assertEqual(block_indication_book.composite_reputational_scores['S00'], block_indication_book.initial_composite_reputational_score)

        # check that an entry was created in the events_reputational_scores dictionary for the traders
        self.assertEqual(block_indication_book.event_reputational_scores['B00'], [])
        self.assertEqual(block_indication_book.event_reputational_scores['S00'], [])

    def test_add_block_indication_function_overwrite(self):

        # create a block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1008, 333, 240))

        # add the block indications
        return_values = []
        for block_indication in block_indications:
            return_values.append(block_indication_book.add_block_indication(block_indication, False))

        self.assertEqual(return_values, [[0, 'Addition'], [1, 'Addition'], [2, 'Overwrite']])
        self.assertEqual(len(block_indication_book.buy_side.orders), 1)
        self.assertEqual(len(block_indication_book.sell_side.orders), 1)
        self.assertEqual(block_indication_book.buy_side.orders[0].__str__(), "BI: [ID=2 T=100.00 B00 Buy Q=1008 P=333 MES=240]")
        self.assertEqual(block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=1 T=100.00 S00 Sell Q=999 P=None MES=None]")

    def test_add_block_indication_function_overwrite_across_sides(self):

        # create a block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Sell', 1008, 333, 240))

        # add the block indications
        return_values = []
        for block_indication in block_indications:
            return_values.append(block_indication_book.add_block_indication(block_indication, False))

        self.assertEqual(return_values, [[0, 'Addition'], [1, 'Addition'], [2, 'Overwrite']])
        self.assertEqual(len(block_indication_book.buy_side.orders), 0)
        self.assertEqual(len(block_indication_book.sell_side.orders), 2)
        self.assertEqual(block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=2 T=100.00 B00 Sell Q=1008 P=333 MES=240]")
        self.assertEqual(block_indication_book.sell_side.orders[1].__str__(), "BI: [ID=1 T=100.00 S00 Sell Q=999 P=None MES=None]")

    def test_trader_has_block_indication_function(self):

        # create a block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))

        for block_indication in block_indications:
            block_indication_book.add_block_indication(block_indication, False)

        self.assertTrue(block_indication_book.trader_has_block_indication('B00'))
        self.assertTrue(block_indication_book.trader_has_block_indication('S00'))
        self.assertFalse(block_indication_book.trader_has_block_indication('B01'))
        self.assertFalse(block_indication_book.trader_has_block_indication('S01'))
        self.assertFalse(block_indication_book.trader_has_block_indication('B02'))
        self.assertFalse(block_indication_book.trader_has_block_indication('S02'))

    def test_book_del_function(self):
        
        # create a block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))

        # add the block indications
        for block_indication in block_indications:
            block_indication_book.add_block_indication(block_indication, False)

        # check the number of block indications
        self.assertEqual(len(block_indication_book.buy_side.orders), 1)
        self.assertEqual(len(block_indication_book.sell_side.orders), 1)

        # delete block indication
        block_indication_book.book_del('B00')

        # check the number of block indications
        self.assertEqual(len(block_indication_book.buy_side.orders), 0)
        self.assertEqual(len(block_indication_book.sell_side.orders), 1)

        # delete block indication
        block_indication_book.book_del('S00')

        # check the number of block indications
        self.assertEqual(len(block_indication_book.buy_side.orders), 0)
        self.assertEqual(len(block_indication_book.sell_side.orders), 0)


    def test_del_block_indication_function(self):

        # create the block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 125, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'B01', 'Buy', 900, 112, 450))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 999, None, None))

        # add the block indications
        for block_indication in block_indications:
            block_indication_book.add_block_indication(block_indication, False)

        # delete a block indication
        block_indication_book.del_block_indication(100.0, block_indications[0], False)

        # check that the remaining block indications are as expected
        self.assertEqual(block_indication_book.buy_side.orders[0].__str__(), "BI: [ID=1 T=100.00 B01 Buy Q=900 P=112 MES=450]")
        self.assertEqual(block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=2 T=100.00 S00 Sell Q=999 P=None MES=None]")

    def test_check_price_match_function(self):
        
        # create the block_indication_book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(block_indication_book.check_price_match(BI1, BI2, 50))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, None, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(block_indication_book.check_price_match(BI1, BI2, 50))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, 6)
        self.assertTrue(block_indication_book.check_price_match(BI1, BI2, 50))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, None, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, 6)
        self.assertTrue(block_indication_book.check_price_match(BI1, BI2, 50))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 51, 6)
        self.assertFalse(block_indication_book.check_price_match(BI1, BI2, 50))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 49, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(block_indication_book.check_price_match(BI1, BI2, 50))

    def test_check_size_match_function(self):
        
        # create the block_indication_book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some BIs and test them
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, None)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertFalse(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 11, 56, None)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        BI2 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 5, 56, 3)
        self.assertFalse(block_indication_book.check_size_match(BI1, BI2))

        BI1 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        BI2 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 7, 56, 3)
        self.assertTrue(block_indication_book.check_size_match(BI1, BI2))

    def test_check_match_function(self):
        
        # create the block_indication_book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, 56, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, 6)
        self.assertTrue(block_indication_book.check_match(BI1, BI2, 50))

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, 50, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 50, 6)
        self.assertTrue(block_indication_book.check_match(BI1, BI2, 50))

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, 49, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 51, 6)
        self.assertFalse(block_indication_book.check_match(BI1, BI2, 50))

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, None, 3)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, 46, None)
        self.assertTrue(block_indication_book.check_match(BI1, BI2, 50))

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 11, None, None)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, None)
        self.assertTrue(block_indication_book.check_match(BI1, BI2, 50))

        # create some BIs
        BI1 = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 6, 49, None)
        BI2 = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, None)
        self.assertFalse(block_indication_book.check_match(BI1, BI2, 50))

    def test_find_matching_block_indications_function(self):

        # create the block ixndication book
        block_indication_book = dark_pool.Block_Indication_Book()
        block_indication_book.MIV = 450

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 499, 25, 450))

        # add the block indications
        for block_indication in block_indications:
            block_indication_book.add_block_indication(block_indication, False)

        # check that there is no match
        self.assertEqual(block_indication_book.find_matching_block_indications(50.0), None)

        # add another block indication
        block_indication_book.add_block_indication(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, None, None), False)

        # check that there is a match
        self.assertEqual(block_indication_book.find_matching_block_indications(50.0), 0)

        # check that the match is as expected
        self.assertEqual(block_indication_book.matches[0]["buy_side_BI"].__str__(), "BI: [ID=0 T=100.00 B00 Buy Q=1024 P=75 MES=500]")
        self.assertEqual(block_indication_book.matches[0]["sell_side_BI"].__str__(), "BI: [ID=2 T=100.00 S00 Sell Q=500 P=None MES=None]")
        self.assertEqual(block_indication_book.matches[0]["buy_side_QBO"], None)
        self.assertEqual(block_indication_book.matches[0]["sell_side_QBO"], None)

    def test_get_block_indication_match_function(self):
        
        # create the block_indication_book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some BIs
        buy_side_BI = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 11, None, None)
        sell_side_BI = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, None)

        block_indication_book.matches[0] = {"buy_side_BI": buy_side_BI, 
                                            "sell_side_BI": sell_side_BI,
                                            "buy_side_QBO": None,
                                            "sell_side_QBO": None}

        returned_match = block_indication_book.get_block_indication_match(0)

        self.assertEqual(returned_match["buy_side_BI"].__str__(), "BI: [ID=-1 T=25.00 B00 Buy Q=11 P=None MES=None]")
        self.assertEqual(returned_match["sell_side_BI"].__str__(), "BI: [ID=-1 T=45.00 S00 Sell Q=11 P=None MES=None]")
        self.assertEqual(returned_match["buy_side_QBO"], None)
        self.assertEqual(returned_match["sell_side_QBO"], None)

    def test_add_qualifying_block_order_function(self):

        # create the block indication book
        block_indication_book = dark_pool.Block_Indication_Book()
        block_indication_book.MIV = 450

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500))
        block_indications.append(dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, None, 500))

        # add the block indications
        for block_indication in block_indications:
            block_indication_book.add_block_indication(block_indication, False)

        # find a match between the block indications
        block_indication_book.find_matching_block_indications(50.0)

        # create some qualifying block orders
        QBO1 = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 1024, 75, 500, 0)
        QBO2 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 500, None, 500, 0)

        
        self.assertEqual(block_indication_book.add_qualifying_block_order(QBO1, False), "First QBO received.")
        self.assertEqual(block_indication_book.add_qualifying_block_order(QBO2, False), "Both QBOs have been received.")

        self.assertEqual(block_indication_book.matches[0]["buy_side_BI"].__str__(), "BI: [ID=0 T=100.00 B00 Buy Q=1024 P=75 MES=500]")
        self.assertEqual(block_indication_book.matches[0]["sell_side_BI"].__str__(), "BI: [ID=1 T=100.00 S00 Sell Q=500 P=None MES=500]")
        self.assertEqual(block_indication_book.matches[0]["buy_side_QBO"].__str__(), "QBO: [ID=0 T=100.00 B00 Buy Q=1024 P=75 MES=500 MID=0]")
        self.assertEqual(block_indication_book.matches[0]["sell_side_QBO"].__str__(), "QBO: [ID=1 T=100.00 S00 Sell Q=500 P=None MES=500 MID=0]")

    def test_marketable_function(self):

        block_indication_book = dark_pool.Block_Indication_Book()

        BI1 = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500)
        QBO1 = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 800, 75, 500, 0)
        self.assertTrue(block_indication_book.marketable(BI1, QBO1))

        BI2 = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, 25, 500)
        QBO2 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 500, None, 500, 0)
        self.assertTrue(block_indication_book.marketable(BI2, QBO2))

        BI3 = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, None, 500)
        QBO3 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 500, 25, 500, 0)
        self.assertFalse(block_indication_book.marketable(BI3, QBO3))

        BI4 = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 800, None, 500)
        QBO4 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 501, None, 499, 0)
        self.assertTrue(block_indication_book.marketable(BI4, QBO4))

        BI5 = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 800, None, None)
        QBO5 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 501, None, 499, 0)
        self.assertFalse(block_indication_book.marketable(BI5, QBO5))

        BI6 = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 800, None, 499)
        QBO6 = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 501, None, 500, 0)
        self.assertFalse(block_indication_book.marketable(BI6, QBO6))

    def test_calculate_event_reputational_score_function(self):
        
        block_indication_book = dark_pool.Block_Indication_Book()
        block_indication_book.event_reputational_scores['B00'] = []

        BI1 = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500)
        QBO1 = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 900, 75, 500, 0)

        BI2 = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 500, 25, 500)
        QBO2 = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 500, None, 500, 0)

        BI3 = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 500, 25, 300)
        QBO3 = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 490, 25, 300)

        self.assertEqual(block_indication_book.calculate_event_reputational_score(BI1, QBO1), 61)
        self.assertEqual(block_indication_book.calculate_event_reputational_score(BI2, QBO2), 100)
        self.assertEqual(block_indication_book.calculate_event_reputational_score(BI3, QBO3), 94)

    def test_calculate_composite_reputational_score_function(self):
        
        block_indication_book = dark_pool.Block_Indication_Book()
        block_indication_book.event_reputational_scores['B00'] = [100,90,80,70,60,50,0]
        self.assertEqual(block_indication_book.calculate_composite_reputational_score('B00'), 66)
        block_indication_book.event_reputational_scores['B00'] = [0,50,60,70,80,90,100]
        self.assertEqual(block_indication_book.calculate_composite_reputational_score('B00'), 63)
        block_indication_book.event_reputational_scores['B00'] = [100,85,0,50,100]
        self.assertEqual(block_indication_book.calculate_composite_reputational_score('B00'), 67)


    def test_update_composite_reputational_scores_function(self):
        
        # create the block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create a match
        block_indication_book.matches[0] = {}
        block_indication_book.matches[0]["buy_side_BI"] = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500)
        block_indication_book.matches[0]["sell_side_BI"] = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, None, 500)
        block_indication_book.matches[0]["buy_side_QBO"] = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 1000, 75, 500, 0)
        block_indication_book.matches[0]["sell_side_QBO"] = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 495, None, 500, 0)

        # create event reputational scores to traders
        block_indication_book.event_reputational_scores['B00'] = []
        block_indication_book.event_reputational_scores['S00'] = []

        # update the composite reputational scores for the traders based on this match
        block_indication_book.update_composite_reputational_scores(0)

        # perform the tests
        self.assertEqual(block_indication_book.event_reputational_scores['B00'], [91])
        self.assertEqual(block_indication_book.event_reputational_scores['S00'], [97])
        self.assertEqual(block_indication_book.composite_reputational_scores['B00'], 91)
        self.assertEqual(block_indication_book.composite_reputational_scores['S00'], 97)

    def test_delete_match_function(self):
        
        # create the block_indication_book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create some BIs
        buy_side_BI = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 11, None, None)
        sell_side_BI = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 11, None, None)

        block_indication_book.matches[0] = {"buy_side_BI": buy_side_BI, 
                                            "sell_side_BI": sell_side_BI,
                                            "buy_side_QBO": None,
                                            "sell_side_QBO": None}

        self.assertNotEqual(block_indication_book.matches.get(0), None)
        block_indication_book.delete_match(0)
        self.assertEqual(block_indication_book.matches.get(0), None)

    def test_create_order_submission_requests_function(self):
        
        # create the block indication book
        block_indication_book = dark_pool.Block_Indication_Book()

        # create a match
        block_indication_book.matches[0] = {}
        block_indication_book.matches[0]["buy_side_BI"] = dark_pool.Block_Indication(100.0, 'B00', 'Buy', 1024, 75, 500)
        block_indication_book.matches[0]["sell_side_BI"] = dark_pool.Block_Indication(100.0, 'S00', 'Sell', 500, None, 500)
        block_indication_book.matches[0]["buy_side_QBO"] = dark_pool.Qualifying_Block_Order(100.0, 'B00', 'Buy', 1000, 75, 500, 0)
        block_indication_book.matches[0]["sell_side_QBO"] = dark_pool.Qualifying_Block_Order(100.0, 'S00', 'Sell', 495, None, 500, 0)

        block_indication_book.composite_reputational_scores['B00'] = 100
        block_indication_book.composite_reputational_scores['S00'] = 100

        self.assertEqual(block_indication_book.create_order_submission_requests(0)["buy_side_OSR"].__str__(), "OSR: [ID=0 T=100.00 B00 Buy Q=1024 P=75 MES=500 MID=0 CRP=100]")
        self.assertEqual(block_indication_book.create_order_submission_requests(0)["sell_side_OSR"].__str__(), "OSR: [ID=3 T=100.00 S00 Sell Q=500 P=None MES=500 MID=0 CRP=100]")

    def test_tape_dump_function(self):
        return

###############################################################################
# tests for Exchange class

class Test_Exchange(unittest.TestCase):

    def test_init_function(self):

        # create an exchange
        exchange = dark_pool.Exchange()

        # check the initialisation
        self.assertEqual(exchange.order_book.tape, [])
        self.assertEqual(exchange.order_book.order_id, 0)
        self.assertEqual(exchange.order_book.buy_side.traders, {})
        self.assertEqual(exchange.order_book.sell_side.traders, {})

    def test_add_order_function_simple(self):
        
        # create an exchange
        exchange = dark_pool.Exchange()

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6))

        # add the orders to the exchange
        self.assertEqual(exchange.add_order(orders[0], False), [0, 'Addition'])
        self.assertEqual(exchange.add_order(orders[1], False), [1, 'Addition'])

        self.assertEqual(len(exchange.order_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)

    def test_add_order_function_overwrite_across_books(self):

        # create an exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 300

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(65.0, 'B00', 'Buy', 350, None, None))
        block_indications.append(dark_pool.Block_Indication(75.0, 'S00', 'Sell', 400, None, None))

        # add the block indications to the exchange
        block_indication_return_values = []
        for block_indication in block_indications:
            block_indication_return_values.append(exchange.add_block_indication(block_indication, False))

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6))

        # add the orders to the exchange
        order_return_values = []
        for order in orders:
            order_return_values.append(exchange.add_order(order, False))

        self.assertEqual(block_indication_return_values, [[0, 'Addition'], [1, 'Addition']])
        self.assertEqual(order_return_values, [[0, 'Overwrite'], [1, 'Overwrite']])
        self.assertEqual(len(exchange.block_indication_book.buy_side.orders), 0)
        self.assertEqual(len(exchange.block_indication_book.sell_side.orders), 0)
        self.assertEqual(len(exchange.order_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)

    def test_add_block_indication_function(self):
        
        # create an exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 300

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(65.0, 'B00', 'Buy', 350, None, None))
        block_indications.append(dark_pool.Block_Indication(75.0, 'S00', 'Sell', 400, None, None))

        # add the block indications to the exchange
        block_indication_return_values = []
        for block_indication in block_indications:
            block_indication_return_values.append(exchange.add_block_indication(block_indication, False))

        self.assertEqual(block_indication_return_values, [[0, 'Addition'], [1, 'Addition']])
        self.assertEqual(len(exchange.block_indication_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.block_indication_book.sell_side.orders), 1)

    def test_add_block_indication_function_overwrite_across_books(self):

        # create an exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 300

        # create some orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, 3))
        orders.append(dark_pool.Order(45.0, 'S00', 'Sell', 11, None, 6))

        # add the orders to the exchange
        order_return_values = []
        for order in orders:
            order_return_values.append(exchange.add_order(order, False))

        # create some block indications
        block_indications = []
        block_indications.append(dark_pool.Block_Indication(65.0, 'B00', 'Buy', 350, None, None))
        block_indications.append(dark_pool.Block_Indication(75.0, 'S00', 'Sell', 400, None, None))

        # add the block indications to the exchange
        block_indication_return_values = []
        for block_indication in block_indications:
            block_indication_return_values.append(exchange.add_block_indication(block_indication, False))

        self.assertEqual(order_return_values, [[0, 'Addition'], [1, 'Addition']])
        self.assertEqual(block_indication_return_values, [[0, 'Overwrite'], [1, 'Overwrite']])
        self.assertEqual(len(exchange.order_book.buy_side.orders), 0)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 0)
        self.assertEqual(len(exchange.block_indication_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.block_indication_book.sell_side.orders), 1)

    def test_add_qualifying_block_order_function(self):
        return

    def test_add_firm_orders_to_order_book(self):
        
        # create an exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 300

        # create some BIs
        buy_side_BI = dark_pool.Block_Indication(25.0, 'B00', 'Buy', 300, None, None)
        sell_side_BI = dark_pool.Block_Indication(45.0, 'S00', 'Sell', 300, None, None)
        buy_side_QBO = dark_pool.Qualifying_Block_Order(55.0, 'B00', 'Buy', 300, None, None, 0)
        sell_side_QBO = dark_pool.Qualifying_Block_Order(65.0, 'S00', 'Sell', 300, None, None, 0)

        exchange.block_indication_book.matches[0] = {   "buy_side_BI": buy_side_BI, 
                                                        "sell_side_BI": sell_side_BI,
                                                        "buy_side_QBO": buy_side_QBO,
                                                        "sell_side_QBO": sell_side_QBO}

        exchange.add_firm_orders_to_order_book(0)

        self.assertEqual(len(exchange.order_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=0 T=55.00 B00 Buy Q=300 QR=300 P=None MES=None]")
        self.assertEqual(exchange.order_book.sell_side.orders[0].__str__(), "Order: [ID=1 T=65.00 S00 Sell Q=300 QR=300 P=None MES=None]")

    def test_del_order_function(self):

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
        self.assertEqual(len(exchange.order_book.buy_side.orders), 1)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)

####################################################################################
# tests for the Trader class

class Test_Trader(unittest.TestCase):

    def test_init_function(self):
        ttype = 'GVWY'
        tid = 'B00'
        balance = 1000
        time = 55.0

        trader = dark_pool.Trader(ttype, tid, balance, time)

        self.assertEqual(trader.ttype, ttype)
        self.assertEqual(trader.trader_id, tid)
        self.assertEqual(trader.balance, balance)
        self.assertEqual(trader.blotter, [])
        self.assertEqual(trader.customer_order, None)
        self.assertEqual(trader.n_quotes, 0)
        self.assertEqual(trader.willing, 1)
        self.assertEqual(trader.able, 1)
        self.assertEqual(trader.birthtime, time)
        self.assertEqual(trader.profitpertime, 0)
        self.assertEqual(trader.n_trades, 0)
        self.assertEqual(trader.lastquote, None)
        self.assertEqual(trader.quantity_traded, 0)

    def test_str_function(self):
        ttype = 'GVWY'
        tid = 'B00'
        balance = 1000
        time = 55.0

        trader = dark_pool.Trader(ttype, tid, balance, time)

        self.assertEqual(trader.__str__(), "[TID B00 type GVWY balance 1000 blotter [] customer order None n_trades 0 profitpertime 0]")

####################################################################################
# testing general functions

class Test_Functions(unittest.TestCase):

    def test_populate_market_function(self):

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

###########################################################################
# the code to be executed if this is the main program

if __name__ == "__main__":
    unittest.main()