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
                    exchange.match_block_indications_and_get_firm_orders(0, traders, price)
            
                # perform all trades possible after each order/BI is added
                exchange.execute_trades(100.0, price)

        # test that the resuls are as expected
        self.assertEqual(len(exchange.order_book.buy_side.orders), 3)
        self.assertEqual(len(exchange.order_book.sell_side.orders), 1)
        self.assertEqual(exchange.order_book.buy_side.orders[0].__str__(), "Order: [ID=1 T=20.00 B01 Buy Q=10 QR=10 P=76 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[1].__str__(), "Order: [ID=0 T=20.00 B00 Buy Q=5 QR=5 P=67 MES=2]")
        self.assertEqual(exchange.order_book.buy_side.orders[2].__str__(), "Order: [ID=2 T=20.00 B02 Buy Q=3 QR=3 P=98 MES=2]")
        self.assertEqual(exchange.order_book.sell_side.orders[0].__str__(), "Order: [ID=8 T=100.00 S03 Sell Q=435 QR=18 P=32 MES=18]")
        self.assertEqual(exchange.block_indication_book.composite_reputational_scores['B03'], 91)
        self.assertEqual(exchange.block_indication_book.composite_reputational_scores['S03'], 91)
        self.assertEqual(exchange.order_book.tape, [{'price': 50.0, 'seller': 'S00', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 11}, {'price': 50.0, 'seller': 'S01', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 4}, {'price': 50.0, 'seller': 'S02', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 12}, {'price': 50.0, 'seller': 'S03', 'BDS': True, 'time': 100.0, 'buyer': 'B03', 'type': 'Trade', 'quantity': 379}, {'price': 50.0, 'seller': 'S03', 'BDS': False, 'time': 100.0, 'buyer': 'B04', 'type': 'Trade', 'quantity': 38}])

###########################################################################
# the code to be executed if this is the main program

def test1():

    # initialise the exchange
    exchange = Exchange()
    exchange.block_indication_book.MIV = 300

    # create some example orders
    orders = []
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))
    orders.append(Order(35.0, 'B01', 'Buy', 10, None, 6))
    orders.append(Order(55.0, 'B02', 'Buy', 3, 53, 1))
    orders.append(Order(75.0, 'B03', 'Buy', 3, 59, None))
    orders.append(Order(65.0, 'B04', 'Buy', 3, 61, 2))
    orders.append(Order(45.0, 'S00', 'Sell', 11, None, 6))
    orders.append(Order(55.0, 'S01', 'Sell', 4, 43, 2))
    orders.append(Order(65.0, 'S02', 'Sell', 6, 48, None))
    orders.append(Order(55.0, 'S03', 'Sell', 6, None, 4))
    orders.append(Order(75.0, 'B00', 'Sell', 8, None, None))
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))

    # add the orders to the exchange
    for order in orders:
        print(exchange.add_order(order, False))

    block_indications = []
    block_indications.append(Block_Indication(35.0, 'B00', 'Buy', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'B01', 'Buy', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'B02', 'Buy', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'S00', 'Sell', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'S01', 'Sell', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'S02', 'Sell', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'B00', 'Sell', 500, None, None))
    block_indications.append(Block_Indication(35.0, 'B00', 'Buy', 500, None, None))


    for block_indication in block_indications:
        print(exchange.add_block_indication(block_indication, False))

    exchange.print_block_indications()
    exchange.print_order_book()

def test2():

    # initialise the exchange
    exchange = Exchange()

    # create some example orders
    orders = []
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))
    orders.append(Order(35.0, 'B01', 'Buy', 10, None, None))
    orders.append(Order(55.0, 'B02', 'Buy', 3, None, None))
    orders.append(Order(75.0, 'B03', 'Buy', 3, None, None))
    orders.append(Order(65.0, 'B04', 'Buy', 3, None, None))
    orders.append(Order(45.0, 'S00', 'Sell', 11, None, None))
    orders.append(Order(55.0, 'S01', 'Sell', 4, None, None))
    orders.append(Order(65.0, 'S02', 'Sell', 6, None, None))
    orders.append(Order(55.0, 'S03', 'Sell', 6, None, None))
    orders.append(Order(75.0, 'B00', 'Sell', 8, None, None))
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))

    
    for order in orders:
        exchange.add_order(order, False)

    exchange.print_order_book()

    exchange.execute_trades(100, 50)

    exchange.print_order_book()


def test3():

    # initialise the exchange
    exchange = Exchange()

    # create some example orders
    orders = []
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))
    orders.append(Order(35.0, 'B01', 'Buy', 10, None, None))
    orders.append(Order(55.0, 'B02', 'Buy', 3, None, None))
    orders.append(Order(75.0, 'B03', 'Buy', 3, None, None))
    orders.append(Order(65.0, 'B04', 'Buy', 3, None, None))
    orders.append(Order(45.0, 'S00', 'Sell', 11, None, None))
    orders.append(Order(55.0, 'S01', 'Sell', 4, None, None))
    orders.append(Order(65.0, 'S02', 'Sell', 6, None, None))
    orders.append(Order(55.0, 'S03', 'Sell', 6, None, None))
    orders.append(Order(75.0, 'B00', 'Sell', 8, None, None))
    orders.append(Order(25.0, 'B00', 'Buy', 5, None, None))

    
    for order in orders:
        exchange.add_order(order, False)

    exchange.print_order_book()

    exchange.execute_trades(100, 50)

    exchange.print_order_book()

if __name__ == "__main__":
    unittest.main()