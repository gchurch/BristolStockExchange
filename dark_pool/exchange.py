from orders import *
from orderbook import *
from block_indication_book import *

# Exchange class. This class is used to bring together the Orderbook class and the Block_Indication_Book class.
class Exchange:

    # constructor method
    def __init__(self):
        # order_book will hold all of the orders made by traders
        self.order_book = Orderbook()
        # block_indication_book will hold all of the block indications made by traders 
        self.block_indication_book = Block_Indication_Book()

    # add an order to the exchange
    def add_order(self, order, verbose):
        # Make sure that what is being added is actually an order
        if(isinstance(order, Order)):
            # Add the order to the exchange
            [order_id, response] = self.order_book.add_order(order, verbose)
            # If the trader already has a block indication on the exchange, then delete it
            if self.block_indication_book.trader_has_block_indication(order.trader_id):
                self.block_indication_book.book_del(order.trader_id)
                response = 'Overwrite'
            # Return the order id and the response
            return [order_id, response]
        else:
            return [-1, "Not an Order."]
    
    # add a block indication to the exchange
    def add_block_indication(self, BI, verbose):
        # Make sure that what is being added is actually a block indication
        if(isinstance(BI, Block_Indication)):
            # Add the block indication to the exchange
            [BI_id, response] = self.block_indication_book.add_block_indication(BI, verbose)
            # If the trader already has an order in the order book, then delete it
            if response != "Block Indication Rejected" and self.order_book.trader_has_order(BI.trader_id):
                self.order_book.book_del(BI.trader_id)
                response = 'Overwrite'
            # Return the block indication ID and the response
            return [BI_id, response]
        else:
            return [-1, "Not a Block Indication."]

    # add a qualifying block order to the exchange
    def add_qualifying_block_order(self, QBO, verbose):
        if(isinstance(QBO, Qualifying_Block_Order)):
            return self.block_indication_book.add_qualifying_block_order(QBO, verbose)
        else:
            return "Not a Qualifying Block Order."

    # convert Qualifying Block Orders into firm orders
    def add_firm_orders_to_order_book(self, match_id):

        # get the QBOs from the match
        full_match = self.block_indication_book.get_block_indication_match(match_id)
        buy_QBO = full_match["buy_QBO"]
        sell_QBO = full_match["sell_QBO"]

        # Here is where the problem lies when I was trying to create the reputational scoring graph
        # The QBOs are converted into orders and added to the order book
        # If these orders cannot match on the order book then the trade doesn't go through
        # However a new composite reputational score has already been calculated.
        # So the event reputational score is updated but a trade doesn't go through, which was confusing me.

        # create orders out of the QBOs
        buy_order = Order(buy_QBO.time,
                               buy_QBO.trader_id,
                               buy_QBO.otype,
                               buy_QBO.quantity,
                               buy_QBO.limit_price,
                               buy_QBO.MES)
        sell_order = Order(sell_QBO.time,
                                sell_QBO.trader_id,
                                sell_QBO.otype,
                                sell_QBO.quantity,
                                sell_QBO.limit_price,
                                sell_QBO.MES)

        # add the orders to the order book
        buy_order.BDS = True
        buy_order.BDS_match_id = match_id
        sell_order.BDS = True
        sell_order.BDS_match_id = match_id
        self.add_order(buy_order, False)
        self.add_order(sell_order, False)


    # match block indications that are lying in the exchange and then convert those block indications 
    # into firm orders
    def match_block_indications_and_get_firm_orders(self, time, traders, price):
        
        # find all block indication matches
        self.block_indication_book.find_all_matching_block_indications(price)

        # go through all matches
        for match_id in self.block_indication_book.matches.keys():

            # get the block indications that were matched
            full_match = self.block_indication_book.get_block_indication_match(match_id)
            buy_BI = full_match["buy_BI"]
            sell_BI = full_match["sell_BI"]

            # send an OSR to each traders and get back a QBO
            OSRs = self.block_indication_book.create_order_submission_requests(match_id)
            buy_QBO = traders[buy_BI.trader_id].get_qualifying_block_order(time, OSRs["buy_OSR"])
            sell_QBO = traders[sell_BI.trader_id].get_qualifying_block_order(time, OSRs["sell_OSR"])

            # add the QBOs to the exchange
            self.block_indication_book.add_qualifying_block_order(buy_QBO, False)
            self.block_indication_book.add_qualifying_block_order(sell_QBO, False)

            # update the reputational scores of the traders in the match
            self.block_indication_book.update_composite_reputational_scores(time, match_id)

            # add the firm orders to the order book.
            self.add_firm_orders_to_order_book(match_id)
            
            # delete the block indication match from the matches dictionary
            self.block_indication_book.delete_match(match_id)


    # write the order_book's tape to the output file
    def tape_dump(self, fname, fmode, tmode):
        self.order_book.tape_dump(fname, fmode, tmode)

    # write the order_book's tape to the output file
    def CRS_history_dump(self, fname, fmode, tmode):
        self.block_indication_book.CRS_history_dump(fname, fmode, tmode)

    # write the order_book's tape to the output file
    def ERS_dump(self, fname, fmode, tmode):
        self.block_indication_book.ERS_dump(fname, fmode, tmode)

    # delete an order from the exchange
    def del_order(self, time, order, verbose):
        return self.order_book.del_order(time, order, verbose)

    def del_block_indication(self, time, order, verbose):
        return self.block_indication_book.del_block_indication(time, order, verbose)

    def execute_trades(self, time, price):
        return self.order_book.execute_trades(time, price)

    # print the current orders in the orders dictionary
    def print_traders(self):
        self.order_book.print_traders()

    # print the current orders in the order_book list
    def print_order_book(self):
        self.order_book.print_order_book()

    def print_block_indication_traders(self):
        self.block_indication_book.print_block_indication_traders()

    def print_block_indications(self):
        self.block_indication_book.print_block_indications()

    def print_composite_reputational_scores(self):
        self.block_indication_book.print_composite_reputational_scores()

    def print_event_reputational_scores(self):
        self.block_indication_book.print_event_reputational_scores()

    def print_qualifying_block_orders(self):
        self.block_indication_book.print_qualifying_block_orders()

    def print_matches(self):
        self.block_indication_book.print_matches()

    def print_tape(self):
        self.order_book.print_tape()
