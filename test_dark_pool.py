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
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

        # test all intialised member variables
        self.assertEqual(orderbook_half.booktype, booktype)
        self.assertEqual(orderbook_half.orders, {})
        self.assertEqual(orderbook_half.lob, {})
        self.assertEqual(orderbook_half.lob_anon, [])
        self.assertEqual(orderbook_half.best_price, None)
        self.assertEqual(orderbook_half.best_tid, None)
        self.assertEqual(orderbook_half.worstprice, worstprice)
        self.assertEqual(orderbook_half.n_orders, 0)
        self.assertEqual(orderbook_half.lob_depth, 0)

    def test_anonymize_lob(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

        # set the order books lob and then call the anonymize function
        orderbook_half.lob = {100: [1, [[25.0, 1, 'B1', 10]]], 150: [1, [[35.0, 1, 'B2', 20]]]}
        orderbook_half.anonymize_lob()

        # test that the anonymized lob is as expected
        self.assertEqual(orderbook_half.lob_anon, [[100, 1], [150, 1]])

    def test_build_lob(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

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
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

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
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

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

    def test_delete_best(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        orderbook_half = dark_pool.Orderbook_half(booktype, worstprice)

        # create instances of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)

        # add the orders to the order book
        orderbook_half.book_add(order1)
        orderbook_half.book_add(order2)

        # build the lob
        orderbook_half.build_lob()

        # delete the best quote
        return_value = orderbook_half.delete_best()

        # test everything is as expected
        self.assertEqual(orderbook_half.lob, {100: [1, [[25.0, 1, 'B1', 10]]]})
        self.assertEqual(orderbook_half.lob_anon, [[100, 1]])
        self.assertEqual(orderbook_half.best_price, 100)
        self.assertEqual(orderbook_half.best_tid, 'B1')
        self.assertEqual(return_value, 'B2')

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

    def test_process_order2(self):

        # create an instance of the Exchange class
        exchange = dark_pool.Exchange()

        # create an instance of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = dark_pool.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = dark_pool.Order('S2', 'Ask', 190, 1, 55.0, 40)

        # add orders to the exchange
        exchange.add_order(order1, False)
        exchange.add_order(order2, False)
        exchange.add_order(order4, False)

        # process order
        return_value = exchange.process_order2(100.0, order3, False)

        # test that the exchange's state is as expected
        self.assertEqual(exchange.bids.lob, {100: [1, [[25.0, 1, 'B1', 0]]]})
        self.assertEqual(exchange.bids.best_price, 100)
        self.assertEqual(exchange.bids.best_tid, 'B1')
        self.assertEqual(exchange.asks.lob, {190: [1, [[55.0, 1, 'S2', 2]]]})
        self.assertEqual(exchange.asks.best_price, 190)
        self.assertEqual(exchange.asks.best_tid, 'S2')
        self.assertEqual(exchange.tape, [{'party2': 'S1', 'party1': 'B2', 'price': 150, 'qty': 1, 'time': 100.0, 'type': 'Trade'}])

        # test the return value
        self.assertEqual(return_value, {'party2': 'S1', 'party1': 'B2', 'price': 150, 'qty': 1, 'time': 100.0, 'type': 'Trade'})

    def test_tape_dump(self):

        # create an instance of the Exchange class
        exchange = dark_pool.Exchange()

        # create some orders
        order1 = dark_pool.Order('B1', 'Bid', 140, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 150, 1, 35.0, 20)
        order3 = dark_pool.Order('S1', 'Ask', 130, 1, 45.0, 30)
        order4 = dark_pool.Order('S2', 'Ask', 120, 1, 55.0, 40)

        # let the exchange process a series of orders
        exchange.process_order2(100.0, order1, False)
        exchange.process_order2(101.0, order2, False)
        exchange.process_order2(102.0, order3, False)
        exchange.process_order2(103.0, order4, False)

        exchange.tape_dump('transactions_test.csv', 'w', 'keep')

        rows = []

        with open('transactions_test.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(row)
        csvfile.close()

        self.assertEqual(rows, [['102.0', ' 150'], ['103.0', ' 140']])

    def test_publish_lob(self):

        exchange = dark_pool.Exchange()

        # create an instance of the Order class
        order1 = dark_pool.Order('B1', 'Bid', 100, 1, 25.0, 10)
        order2 = dark_pool.Order('B2', 'Bid', 130, 1, 35.0, 20)
        order3 = dark_pool.Order('S1', 'Ask', 140, 1, 45.0, 30)
        order4 = dark_pool.Order('S2', 'Ask', 170, 1, 55.0, 40)

        # process the orders
        exchange.process_order2(100.0, order1, False)
        exchange.process_order2(101.0, order2, False)
        exchange.process_order2(102.0, order3, False)
        exchange.process_order2(103.0, order4, False)

        # test that the publish_lob function produces the expected return value
        self.assertEqual(exchange.publish_lob(104.0, False), {'QID': 4, 'tape': [], 'bids': {'lob': [[100, 1], [130, 1]], 'worst': 1, 'best': 130, 'n': 2}, 'asks': {'lob': [[140, 1], [170, 1]], 'worst': 1000, 'best': 140, 'n': 2}, 'time': 104.0})  



if __name__ == "__main__":
    unittest.main()