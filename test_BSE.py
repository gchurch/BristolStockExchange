import unittest
import BSE
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
        order = BSE.Order(tid, otype, price, qty, time, qid)

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
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # test all intialised member variables
        self.assertEqual(instance.booktype, booktype)
        self.assertEqual(instance.orders, {})
        self.assertEqual(instance.lob, {})
        self.assertEqual(instance.lob_anon, [])
        self.assertEqual(instance.best_price, None)
        self.assertEqual(instance.best_tid, None)
        self.assertEqual(instance.worstprice, worstprice)
        self.assertEqual(instance.n_orders, 0)
        self.assertEqual(instance.lob_depth, 0)

    def test_anonymize_lob(self):
        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        instance.lob = {100: [1, [[25.0, 1, 'B1', 10]]], 150: [1, [[35.0, 1, 'B2', 20]]]}
        instance.anonymize_lob()

        self.assertEqual(instance.lob_anon, [[100, 1], [150, 1]])

    def test_build_lob(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the order to the order book
        instance.book_add(order1)
        instance.book_add(order2)

        # build the lob
        instance.build_lob()

        # test the lob
        self.assertEqual(instance.lob, {100: [1, [[25.0, 1, 'B1', 10]]], 150: [1, [[35.0, 1, 'B2', 20]]]})
        self.assertEqual(instance.best_price, 150)
        self.assertEqual(instance.best_tid, 'B2')

    def test_book_add(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the order to the order book
        instance.book_add(order1)
        instance.book_add(order2)

        # test order book after adding an order
        self.assertEqual(instance.orders, {'B1': order1, 'B2': order2})
        self.assertEqual(instance.n_orders, 2)


    def test_book_del(self):
        
        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the order to the order book and then delete it
        instance.book_add(order1)
        instance.book_add(order2)

        # delete order1
        instance.book_del(order1)

        # test
        self.assertEqual(instance.orders, {'B2': order2})
        self.assertEqual(instance.n_orders, 1)

        # delete order2
        instance.book_del(order2)

        # test
        self.assertEqual(instance.orders, {})
        self.assertEqual(instance.n_orders, 0)

    def test_delete_best(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the order to the order book
        instance.book_add(order1)
        instance.book_add(order2)

        instance.build_lob()
        instance.delete_best()

        # test function
        self.assertEqual(instance.lob, {100: [1, [[25.0, 1, 'B1', 10]]]})
        self.assertEqual(instance.lob_anon, [[100, 1]])
        self.assertEqual(instance.best_price, 100)
        self.assertEqual(instance.best_tid, 'B1')

################################################################################
# tests for the Orderbook class

class Test_Orderbook(unittest.TestCase):

    def test_init(self):

        orderbook = BSE.Orderbook()

        self.assertEqual(orderbook.tape, [])
        self.assertEqual(orderbook.quote_id, 0)
        self.assertEqual(orderbook.bids.lob, {})
        self.assertEqual(orderbook.asks.lob, {})

###############################################################################
# tests for Exchange class

class Test_Exchange(unittest.TestCase):

    def test_add_init(self):

        exchange = BSE.Exchange()

        self.assertEqual(exchange.tape, [])
        self.assertEqual(exchange.quote_id, 0)
        self.assertEqual(exchange.bids.lob, {})
        self.assertEqual(exchange.asks.lob, {})

    def test_add_order(self):
        
        # create an instance of the exchange class
        exchange = BSE.Exchange()

        # create instances of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = BSE.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = BSE.Order('S2', 'Ask', 190, 1, 55.0, 40)

        # add the orders to the exchange
        exchange.add_order(order1, False)
        exchange.add_order(order2, False)
        exchange.add_order(order3, False)
        exchange.add_order(order4, False)

        # test that the exchange's state is as expected
        self.assertEqual(exchange.bids.lob, {100: [1, [[25.0, 1, 'B1', 0]]], 150: [1, [[35.0, 1, 'B2', 1]]]})
        self.assertEqual(exchange.bids.best_price, 150)
        self.assertEqual(exchange.bids.best_tid, 'B2')
        self.assertEqual(exchange.asks.lob, {140: [1, [[45.0, 1, 'S1', 2]]], 190: [1, [[55.0, 1, 'S2', 3]]]})
        self.assertEqual(exchange.asks.best_price, 140)
        self.assertEqual(exchange.asks.best_tid, 'S1')

    def test_del_order(self):

        # create an instance of the Exchange class
        exchange = BSE.Exchange()

        # create instances of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = BSE.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = BSE.Order('S2', 'Ask', 190, 1, 55.0, 40)

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

    def test_process_order2(self):

        # create an instance of the Exchange class
        exchange = BSE.Exchange()

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = BSE.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = BSE.Order('S2', 'Ask', 190, 1, 55.0, 40)

        # add orders to the exchange
        exchange.add_order(order1, False)
        exchange.add_order(order2, False)
        exchange.add_order(order4, False)

        # process order
        exchange.process_order2(100.0, order3, False)

        # test that the exchange's state is as expected
        self.assertEqual(exchange.bids.lob, {100: [1, [[25.0, 1, 'B1', 0]]]})
        self.assertEqual(exchange.bids.best_price, 100)
        self.assertEqual(exchange.bids.best_tid, 'B1')
        self.assertEqual(exchange.asks.lob, {190: [1, [[55.0, 1, 'S2', 2]]]})
        self.assertEqual(exchange.asks.best_price, 190)
        self.assertEqual(exchange.asks.best_tid, 'S2')
        self.assertEqual(exchange.tape, [{'party2': 'S1', 'party1': 'B2', 'price': 150, 'qty': 1, 'time': 100.0, 'type': 'Trade'}])

    def test_tape_dump(self):

        # create an instance of the Exchange class
        exchange = BSE.Exchange()

        # create some orders
        order1 = BSE.Order('B1', 'Bid', 140, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = BSE.Order('S1', 'Ask', 130, 1, 45.0, 30)
        order4 = BSE.Order('S2', 'Ask', 120, 1, 55.0, 40)

        # let the exchange process a series of orders
        exchange.process_order2(100.0, order1, False)
        exchange.process_order2(101.0, order2, False)
        exchange.process_order2(102.0, order3, False)
        exchange.process_order2(103.0, order4, False)

        exchange.tape_dump('test.csv', 'w', 'keep')

        rows = []

        with open('test.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(row)
        csvfile.close()

        self.assertEqual(rows, [['102.0', ' 150'], ['103.0', ' 140']])

    def test_publish_lob(self):

        exchange = BSE.Exchange()

        # create an instance of the Order class
        order1 = BSE.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = BSE.Order('B2', 'Bid', 130, 1, 35.0, 20)
        order3 = BSE.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = BSE.Order('S2', 'Ask', 170, 1, 55.0, 40)

        exchange.process_order2(100.0, order1, False)
        exchange.process_order2(101.0, order2, False)
        exchange.process_order2(102.0, order3, False)
        exchange.process_order2(103.0, order4, False)

        self.assertEqual(exchange.publish_lob(104.0, False), {'QID': 4, 'tape': [], 'bids': {'lob': [[100, 1], [130, 1]], 'worst': 1, 'best': 130, 'n': 2}, 'asks': {'lob': [[140, 1], [170, 1]], 'worst': 1000, 'best': 140, 'n': 2}, 'time': 104.0})  


###########################################################################
# the code to be executed if this is the main program

if __name__ == "__main__":
    unittest.main()