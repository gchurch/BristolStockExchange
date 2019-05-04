import unittest
import dark_pool


class Test_Integration(unittest.TestCase):

    def test_order_and_block_indication_submission_and_trading(self):

		# initialise the exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 100
        exchange.MIV = 100
        exchange.RST = 55

        # create the trader specs
        buyers_spec = [('GVWY_test',12)]
        sellers_spec = buyers_spec
        traders_spec = {'sellers':sellers_spec, 'buyers':buyers_spec, 'BI_threshold':600}

        # create a bunch of traders
        traders = {}
        trader_stats = dark_pool.populate_market(traders_spec, traders, True, False)

        # create some customer orders
        customer_orders = []
        customer_orders.append(dark_pool.Customer_Order(25.0, 'B00', 'Buy', 67, 5,))
        customer_orders.append(dark_pool.Customer_Order(35.0, 'B01', 'Buy', 76, 10))
        customer_orders.append(dark_pool.Customer_Order(55.0, 'B02', 'Buy', 98, 3))
        customer_orders.append(dark_pool.Customer_Order(75.0, 'B03', 'Buy', 73, 389))
        customer_orders.append(dark_pool.Customer_Order(85.0, 'B04', 'Buy', 62, 65))
        customer_orders.append(dark_pool.Customer_Order(45.0, 'S00', 'Sell', 23, 11))
        customer_orders.append(dark_pool.Customer_Order(55.0, 'S01', 'Sell', 43, 4))
        customer_orders.append(dark_pool.Customer_Order(60.0, 'S02', 'Sell', 11, 12))
        customer_orders.append(dark_pool.Customer_Order(65.0, 'S03', 'Sell', 32, 445))

        # assign customer orders to traders
        for customer_order in customer_orders:
            traders[customer_order.trader_id].add_order(customer_order, False)

        # The price for all traders. In the future this will be equal to the PMP
        price = 50.0

        # add each trader's order to the exchange
        for tid in sorted(traders.keys()):

        	# configure the traders for the test
            traders[tid].BI_threshold = 100
 
            # get the order from the trader
            order = traders[tid].getorder(20.0)

            # add the order/BI to the exchange
            if order != None:
                if isinstance(order, dark_pool.Order):
                    exchange.add_order(order, False)
                elif isinstance(order, dark_pool.Block_Indication):
                    exchange.add_block_indication(order, False)
                    # check if there is a match between block indications
                    exchange.match_block_indications_and_get_firm_orders(20, traders, price)
            
                # perform all trades possible after each order/BI is added
                exchange.execute_trades(100.0, price)

        # test that the resuls are as expected
        self.assertEqual(len(exchange.order_book.buy_side.orders), 3)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=1 T=20.00 B01 Buy Q=10 QR=10 P=76 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[1].__str__(), "Order: [ID=0 T=20.00 B00 Buy Q=5 QR=5 P=67 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[2].__str__(), "Order: [ID=2 T=20.00 B02 Buy Q=3 QR=3 P=98 MES=2]")
        self.assertEqual(exchange.order_book.sell_side.orders[0].__str__(), "Order: [ID=8 T=20.00 S03 Sell Q=435 QR=18 P=32 MES=18]")
        self.assertEqual(exchange.block_indication_book.composite_reputational_scores['B03'], 61)
        self.assertEqual(exchange.block_indication_book.composite_reputational_scores['S03'], 61)
        self.assertEqual(exchange.order_book.tape, [{'price': 50.0, 'seller': 'S00', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 11}, {'price': 50.0, 'seller': 'S01', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 4}, {'price': 50.0, 'seller': 'S02', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 12}, {'price': 50.0, 'seller': 'S03', 'BDS': True, 'time': 100.0, 'buyer': 'B03', 'type': 'Trade', 'quantity': 379}, {'price': 50.0, 'seller': 'S03', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 38}])




    def test_only_one_order_or_block_indication_in_the_exchange(self):
        # initialise the exchange
        exchange = dark_pool.Exchange()
        exchange.block_indication_book.MIV = 300

        # create some example orders
        orders = []
        orders.append(dark_pool.Order(25.0, 'B00', 'Buy', 5, None, None))
        orders.append(dark_pool.Order(35.0, 'B01', 'Buy', 10, None, 6))
        orders.append(dark_pool.Order(55.0, 'B02', 'Buy', 3, 53, 1))
        orders.append(dark_pool.Order(75.0, 'B03', 'Buy', 3, 59, None))
        orders.append(dark_pool.Order(65.0, 'B04', 'Buy', 3, 61, 2))

        responses = []

        # add the orders to the exchange
        for order in orders:
            responses.append(exchange.add_order(order, False))

        block_indications = []
        block_indications.append(dark_pool.Block_Indication(35.0, 'B00', 'Buy', 123, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'B01', 'Buy', 564, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'B02', 'Buy', 877, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'S00', 'Sell', 422, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'S01', 'Sell', 558, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'S02', 'Sell', 924, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'B00', 'Sell', 458, None, None))
        block_indications.append(dark_pool.Block_Indication(35.0, 'S02', 'Sell', 358, None, None))


        for block_indication in block_indications:
            responses.append(exchange.add_block_indication(block_indication, False))

        # test that the responses are as expected
        self.assertEqual(responses, [[0, 'Addition'], [1, 'Addition'], [2, 'Addition'], [3, 'Addition'], [4, 'Addition'], [-1, 'Block Indication Rejected'], [0, 'Overwrite'], [1, 'Overwrite'], [2, 'Addition'], [3, 'Addition'], [4, 'Addition'], [5, 'Overwrite'], [6, 'Overwrite']])
        
        # test that the order book is as expected
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=4 T=65.00 B04 Buy Q=3 QR=3 P=61 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[1].__str__(), "Order: [ID=3 T=75.00 B03 Buy Q=3 QR=3 P=59 MES=None]")

        # test that the block indication book is as expected
        self.assertEqual(exchange.block_indication_book.buy_side.orders[0].__str__(), "BI: [ID=1 T=35.00 B02 Buy Q=877 P=None MES=None]")
        self.assertEqual(exchange.block_indication_book.buy_side.orders[1].__str__(), "BI: [ID=0 T=35.00 B01 Buy Q=564 P=None MES=None]")
        self.assertEqual(exchange.block_indication_book.sell_side.orders[0].__str__(), "BI: [ID=3 T=35.00 S01 Sell Q=558 P=None MES=None]")
        self.assertEqual(exchange.block_indication_book.sell_side.orders[1].__str__(), "BI: [ID=5 T=35.00 B00 Sell Q=458 P=None MES=None]")
        self.assertEqual(exchange.block_indication_book.sell_side.orders[2].__str__(), "BI: [ID=2 T=35.00 S00 Sell Q=422 P=None MES=None]")
        self.assertEqual(exchange.block_indication_book.sell_side.orders[3].__str__(), "BI: [ID=6 T=35.00 S02 Sell Q=358 P=None MES=None]")


###########################################################################
# the code to be executed if this is the main program

if __name__ == "__main__":
    unittest.main()