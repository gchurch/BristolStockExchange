import unittest
import BSE

class TestBSE(unittest.TestCase):

    def test_order(self):
        tid = 5
        otype = 'Bid'
        price = 100
        qty = 1
        time = 25.0
        qid = 10

        order = BSE.Order(tid, otype, price, qty, time, qid)

        self.assertEqual(order.tid, tid)
        self.assertEqual(order.otype, otype)
        self.assertEqual(order.price, price)
        self.assertEqual(order.qty, qty)
        self.assertEqual(order.time, time)
        self.assertEqual(order.qid, qid)


if __name__ == "__main__":
    unittest.main()