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

    def test_book_add(self):

        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order = BSE.Order('B5', 'Bid', 100, 1, 25.0, 10)

        # add the order to the order book
        instance.book_add(order)

        # test order book after adding an order
        self.assertEqual(instance.orders, {'B5': order})
        self.assertEqual(instance.n_orders, 1)


    def test_book_del(self):
        
        # create an instance of the Orderbook_half class
        booktype = "Bid"
        worstprice = 200
        instance = BSE.Orderbook_half(booktype, worstprice)

        # create an instance of the Order class
        order = BSE.Order('B5', 'Bid', 100, 1, 25.0, 10)

        # add the order to the order book and then delete it
        instance.book_add(order)
        instance.book_del(order)

        # test that the order book is empty
        self.assertEqual(instance.orders, {})
        self.assertEqual(instance.n_orders, 0)


if __name__ == "__main__":
    unittest.main()