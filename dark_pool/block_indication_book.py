from orders import *
from orderbook_half import *

import math

# Block Indication Book class for a single instrument. The class holds and performs operations with 
# received block indications
class Block_Indication_Book:

    # constructer function for the Block_Indication_Book class
    def __init__(self):
        # The buy side contains all of the block indications to buy
        self.buy_side = Orderbook_half('Buy')
        # The sell side contains all of the block indications to sell
        self.sell_side = Orderbook_half('Sell')
        # The Minimum Indication Value (MIV) is the quantity that a block indication must be greater
        # than in order to be accepted
        self.MIV = 500
        # ID to be given to next Block Indication
        self.BI_id = 0
        # ID to be given to next Qualifying Block Order received
        self.QBO_id = 0
        # ID to be given to the next OSR created
        self.OSR_id = 0
        # The composite_reputational_scores dictionary contains the composite reputational score for each trader. 
        self.composite_reputational_scores = {}
        # The event_reputation_scores dictionary contains the last 50 event reputational scores for each trader.
        self.event_reputational_scores = {}
        # the initial composite reputational score given to each trader
        self.initial_reputational_score = 80
        # the Reputational Score Threshold (RST). All traders with a composite reputational score below this threshold
        # are no longer able to use the block discovery service
        self.RST = 55
        # A dictionary to hold matched BIs and the corresponding QBOs
        self.matches = {}
        # ID to be given to the matching of two block indications
        self.match_id = 0
        # The tape contains the history of block indications sent to the exchange
        self.tape = []
        # The entire history of each trader's score
        self.composite_reputational_scores_history = {}

    
    # Add a block indication to the exchange
    def add_block_indication(self, BI, verbose):

        # if a new trader, then give it an initial reputational score
        if self.composite_reputational_scores.get(BI.trader_id) == None:
            self.composite_reputational_scores[BI.trader_id] = self.initial_reputational_score
            self.event_reputational_scores[BI.trader_id] = [self.initial_reputational_score for i in range(0,50)]
            self.composite_reputational_scores_history[BI.trader_id] = [(0, self.initial_reputational_score)]

        # the quantity of the order must be greater than the MIV
        # the trader must also have a composite reputational score lower than the RST
        if BI.quantity >= self.MIV and self.composite_reputational_scores.get(BI.trader_id) >= self.RST:

            # give an ID to the block indication
            BI.id = self.BI_id
            self.BI_id = BI.id + 1

            # add the block indication to the correct order book
            if BI.otype == 'Buy':
                response=self.buy_side.book_add(BI)
                # If the trader already has a block indication on the sell side, then delete it
                if self.sell_side.trader_has_order(BI.trader_id):
                    self.sell_side.book_del(BI.trader_id)
                    response = 'Overwrite'

            elif BI.otype == 'Sell':
                response=self.sell_side.book_add(BI)
                # If the trader already has a block indication on the buy side, then delete it
                if self.buy_side.trader_has_order(BI.trader_id):
                    self.buy_side.book_del(BI.trader_id)
                    response = 'Overwrite'

            # return the block indication id and the response
            return [BI.id, response]

        # if the block indication was rejected then return the message
        return [-1, "Block Indication Rejected"]

    # check whether a given trader currently has a block indication
    def trader_has_block_indication(self, trader_id):
        if self.buy_side.trader_has_order(trader_id) or self.sell_side.trader_has_order(trader_id):
            return True
        else:
            return False

    # detete all block indications made by a given trader
    def book_del(self, trader_id):
        self.buy_side.book_del(trader_id)
        self.sell_side.book_del(trader_id)

    # delete block indication
    def del_block_indication(self, time, BI, verbose):
        # delete a trader's order from the exchange, update all internal records
        if BI.otype == 'Buy':
            self.buy_side.book_del(BI.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'BI': BI }
            self.tape.append(cancel_record)

        elif BI.otype == 'Sell':
            self.sell_side.book_del(BI.trader_id)
            cancel_record = { 'type': 'Cancel', 'time': time, 'BI': BI }
            self.tape.append(cancel_record)
        else:
            sys.exit('bad order type in del_block_indication()')

    # check that two block indications match in terms of their price
    def check_price_match(self, buy_BI, sell_BI, price):

        if buy_BI.limit_price == None and sell_BI.limit_price == None:
            return True

        elif buy_BI.limit_price != None and sell_BI.limit_price == None:
            if buy_BI.limit_price >= price:
                return True

        elif buy_BI.limit_price == None and sell_BI.limit_price != None:
            if sell_BI.limit_price <= price:
                return True

        elif buy_BI.limit_price != None and sell_BI.limit_price != None:
            if buy_BI.limit_price >= price and sell_BI.limit_price <= price:
                return True

        return False

    # check that two block indications match in terms of their size
    def check_size_match(self, buy_BI, sell_BI):

        if buy_BI.MES == None and sell_BI.MES == None:
            return True

        elif buy_BI.MES != None and sell_BI.MES == None:
            if sell_BI.quantity >= buy_BI.MES:
                return True

        elif buy_BI.MES == None and sell_BI.MES != None:
            if buy_BI.quantity >= sell_BI.MES:
                return True

        elif buy_BI.MES != None and sell_BI.MES != None:
            if buy_BI.quantity >= sell_BI.MES and sell_BI.quantity >= buy_BI.MES:
                return True

        return False

    # check that two block indications match
    def check_match(self, buy_BI, sell_BI, price):
        # check that both the order size and the price match
        return self.check_price_match(buy_BI, sell_BI, price) and self.check_size_match(buy_BI, sell_BI)

    # attempt to find two matching block indications
    def find_matching_block_indications(self, price):
        
        # get the buy block indications list and sell block indications list
        buy_BIs = self.buy_side.get_orders()
        sell_BIs = self.sell_side.get_orders()

        # starting with the buy side first
        for buy_BI in buy_BIs:
            for sell_BI in sell_BIs:
                # check if the two block indications match
                if self.check_match(buy_BI, sell_BI, price):
                    
                    # Add the matched BIs to the matches dictionary
                    self.matches[self.match_id] = {
                        "buy_BI": buy_BI, 
                        "sell_BI": sell_BI,
                        "buy_QBO": None,
                        "sell_QBO": None
                    }

                    # get the current match id
                    match_id = self.match_id

                    # increment the book's match_id counter
                    self.match_id += 1

                    # delete these block indications from the block indication book
                    self.del_block_indication(0, buy_BI, False)
                    self.del_block_indication(0, sell_BI, False)

                    # return the match id
                    return match_id

        # if no match was found then return None
        return None

    # attempt to find two matching block indications
    def find_all_matching_block_indications(self, price):

        match_id = self.find_matching_block_indications(price)

        while match_id != None:
            match_id = self.find_matching_block_indications(price)

    # return a match given the ID
    def get_block_indication_match(self, match_id):
        return self.matches.get(match_id)

    # create the order submissions requests given a match between two block indications
    def create_order_submission_requests(self, match_id):
        # Get the block indications.
        buy_BI = self.matches[match_id]["buy_BI"]
        sell_BI = self.matches[match_id]["sell_BI"]

        # Get the composite reputational scores.
        buy_CRP = self.composite_reputational_scores[buy_BI.trader_id]
        sell_CRP = self.composite_reputational_scores[sell_BI.trader_id]
        
        # create the buy side OSR
        buy_OSR = Order_Submission_Request(self.OSR_id,
                                                buy_BI.time,
                                                buy_BI.trader_id,
                                                buy_BI.otype,
                                                buy_BI.quantity,
                                                buy_BI.limit_price,
                                                buy_BI.MES,
                                                match_id,
                                                buy_CRP)

        # increment the OSR id counter
        self.OSR_id += 1

        # create the sell side OSR
        sell_OSR = Order_Submission_Request(self.OSR_id,
                                                 sell_BI.time,
                                                 sell_BI.trader_id,
                                                 sell_BI.otype,
                                                 sell_BI.quantity,
                                                 sell_BI.limit_price,
                                                 sell_BI.MES,
                                                 match_id,
                                                 sell_CRP)

        # increment the OSR id counter
        self.OSR_id += 1

        # return both OSRs in a dicitionary
        return {"buy_OSR": buy_OSR, "sell_OSR": sell_OSR}

    # add a Qualifying Block Order (QBO). QBOs are added to the appropriate entry in the matches dictionary.
    def add_qualifying_block_order(self, QBO, verbose):

        # give each qualifying block order its own unique id
        QBO.id = self.QBO_id
        self.QBO_id += 1

        # get the match id for the orginally matched block indications
        match_id = QBO.match_id

        # add the qualifying block order to the match in the matches dictionary
        if self.matches.get(match_id) != None:
            if QBO.otype == 'Buy':
                self.matches[match_id]["buy_QBO"] = QBO
            elif QBO.otype == "Sell":
                self.matches[match_id]["sell_QBO"] = QBO
        else:
            return "Incorrect match id."
        
        # check if both QBOs have been received
        if self.matches[match_id]["buy_QBO"] and self.matches[match_id]["sell_QBO"]:
            return "Both QBOs have been received."
        else:
            return "First QBO received."

    # Compare a QBO with a BI to see whether or not its price is marketable
    def marketable_price(self, BI, QBO):

        if BI.limit_price == None and QBO.limit_price == None:
            return True

        elif BI.limit_price != None and QBO.limit_price == None:
            return True

        elif BI.limit_price != None and QBO.limit_price != None:
            if BI.otype == 'Buy':
                if QBO.limit_price >= BI.limit_price:
                    return True
            if BI.otype == 'Sell':
                if QBO.limit_price <= BI.limit_price:
                    return True

        return False

    # Compare a QBO with a BI to see whether or not its size is marketable
    def marketable_size(self, BI, QBO):

        if BI.MES == None and QBO.MES == None:
            return True

        elif BI.MES != None and QBO.MES == None:
            return True

        elif BI.MES != None and QBO.MES != None:
            if QBO.MES <= BI.MES:
                return True

        return False


    # compare a QBO with its BI to see whether it is marketable
    def marketable(self, BI, QBO):
        return self.marketable_price(BI, QBO) and self.marketable_size(BI, QBO)

    # calculate the reputational score of a trader for a single event. If the QBO is not marketable, then the
    # event reputation score is 0. If the QBO is marketable then score will be between 50 and 100
    def calculate_event_reputational_score(self, BI, QBO):

        # Check that the QBO is marketable
        if self.marketable(BI, QBO):

            event_reputational_score = 100

            # calculate the difference between the QBO quantity and the BI quantity as a decimal
            quantity_dec_diff = (float(BI.quantity) - float(QBO.quantity)) / float(BI.quantity)

            # if the QBO quantity is less than the BI quantity then decrease score
            # The function used here is y = 77.1(e^x - 1)
            if quantity_dec_diff > 0:
                event_reputational_score -= round(77.1 * (math.exp(quantity_dec_diff) - 1))

            # Make sure that the score is not less than 50
            if event_reputational_score < 50: 
                event_reputational_score = 50

        # If the QBO is not marketable then the score is 0
        else:
            event_reputational_score = 0

        # Add this event reputational score to the dictionary containing the last 50 event reputational scores
        # for each trader
        self.event_reputational_scores[BI.trader_id].insert(0,event_reputational_score)
        # make sure that the list only contains the last 50 event reputational scores
        self.event_reputational_scores[BI.trader_id] = self.event_reputational_scores[BI.trader_id][:50]

        # return the score
        return event_reputational_score

    # Calculate a trader's composite reputational score.
    # The most recent event reputational score has a weighting of 50, 
    # the next most recent 49, and so on
    def calculate_composite_reputational_score(self, tid):

        # The current weighting
        weighting = 50
        # The sum of the event reputational scores multiplied by their weighting
        total = 0.0

        for i in range(0, 50):
            total += weighting * self.event_reputational_scores[tid][i]
            weighting -= 1

        # Calculate the composite reputational score rounded to the nearest integer
        composite_reputational_score = round(total / 1275.0)

        # return the composite reputational score
        return composite_reputational_score
        

    # update both traders' reputation score given this matching event
    def update_composite_reputational_scores(self, time, match_id):

        # get the BIs and the QBOs from the matches dictionary item
        buy_BI = self.matches[match_id]["buy_BI"]
        sell_BI = self.matches[match_id]["sell_BI"]
        buy_QBO = self.matches[match_id]["buy_QBO"]
        sell_QBO = self.matches[match_id]["sell_QBO"]

        # calculate the event reputation scores (they will be added to list of event reputational scores for each trader)
        self.calculate_event_reputational_score(buy_BI, buy_QBO)
        self.calculate_event_reputational_score(sell_BI, sell_QBO)

        # update the traders' reputational score
        buyer_composite_reputational_score = self.calculate_composite_reputational_score(buy_BI.trader_id)
        seller_composite_reputational_score = self.calculate_composite_reputational_score(sell_BI.trader_id)
        self.composite_reputational_scores[buy_BI.trader_id] = buyer_composite_reputational_score
        self.composite_reputational_scores[sell_BI.trader_id] = seller_composite_reputational_score

        # add the scores to the trader history
        self.composite_reputational_scores_history[buy_BI.trader_id].append((time, buyer_composite_reputational_score))
        self.composite_reputational_scores_history[sell_BI.trader_id].append((time, seller_composite_reputational_score))

    # delete a match from the matches dictonary given the match ID
    def delete_match(self, match_id):
        del(self.matches[match_id])

    # write the composite reputational scores history to an output file
    def CRS_history_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)

        # find the length of the longest list of scores
        highest_length = 0
        for trader in self.composite_reputational_scores_history.keys():
            this_length = len(self.composite_reputational_scores_history[trader])
            if this_length > highest_length:
                highest_length = this_length

        # write the column names
        for trader in sorted(self.composite_reputational_scores_history.keys()):
            dumpfile.write('%s: %d scores,,' % (trader, len(self.composite_reputational_scores_history[trader])))
        dumpfile.write('\n')
        for i in range(0, len(self.composite_reputational_scores_history)):
            dumpfile.write('time,score,')
        dumpfile.write('\n')

        # write each row containing a time and score for each trader
        for i in range(0, highest_length):
            for trader in sorted(self.composite_reputational_scores_history.keys()):
                if i < len(self.composite_reputational_scores_history[trader]):
                    (time, score) = self.composite_reputational_scores_history[trader][i]
                    dumpfile.write('%.2f, %d,' % (time, score))
                else:
                    dumpfile.write(',,')
            dumpfile.write('\n')

        # clost the file
        dumpfile.close()

        if tmode == 'wipe':
            self.tape = []

    # write the composite reputational scores history to an output file
    def ERS_dump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)

        # write the column names
        for trader in sorted(self.event_reputational_scores.keys()):
            dumpfile.write('%s,,' % trader)
        dumpfile.write('\n')
        for i in range(0, len(self.event_reputational_scores)):
            dumpfile.write('time,score,')
        dumpfile.write('\n')

        # write each row containing a time and score for each trader
        for i in range(0, 50):
            for trader in sorted(self.event_reputational_scores.keys()): 
                score = self.event_reputational_scores[trader][i]
                dumpfile.write('%d,' % score)
            dumpfile.write('\n')

        # clost the file
        dumpfile.close()

        if tmode == 'wipe':
            self.tape = []

    # print the composite reputational score of all known traders
    def print_composite_reputational_scores(self):
        print("Reputational scores:")
        for key in self.composite_reputational_scores:
            print("%s : %d" % (key, self.composite_reputational_scores[key]))
        print("")

    # print the event reputational scores of all known traders
    def print_event_reputational_scores(self):
        print("Event reputational scores:")
        for key in self.event_reputational_scores:
            print "%s:" % key,
            for score in self.event_reputational_scores[key]:
                print "%d" % score,
            print("")

    # print all traders that currently have block indications
    def print_traders(self):
        print("Buy orders:")
        self.buy_side.print_traders()
        print("Sell orders:")
        self.sell_side.print_traders()

    # print the current block indications
    def print_block_indications(self):
        print("Block Indications:")
        print("Buy side:")
        self.buy_side.print_orders()
        print("Sell side:")
        self.sell_side.print_orders()
        print("")

    # print the current matches
    def print_matches(self):
        print("Matches:")
        for key in self.matches.keys():
            print("Match id: %d" % key)
            print(self.matches[key]["buy_BI"])
            print(self.matches[key]["sell_BI"])
            if self.matches[key]["buy_QBO"]:
                print(self.matches[key]["buy_QBO"])
            if self.matches[key]["sell_QBO"]:
                print(self.matches[key]["sell_QBO"])
        print("")
