import unittest
import BSE

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
        order2 = BSE.Order('B2', 'Ask', 150, 1, 35.0, 20)

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
        order2 = BSE.Order('B2', 'Ask', 150, 1, 35.0, 20)

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
        order2 = BSE.Order('B2', 'Ask', 150, 1, 35.0, 20)

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
        order2 = BSE.Order('B2', 'Ask', 150, 1, 35.0, 20)

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


if __name__ == "__main__":
    unittest.main()