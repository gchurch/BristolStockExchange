# a customer order which is given to a trader to complete
class Customer_Order:

    def __init__(self, time, tid, otype, price, qty):
        self.time = time      # the time the customer order was issued
        self.trader_id = tid        # the trader i.d. that this order is for
        self.otype = otype    # the order type of the customer order i.e. buy/sell
        self.price = price    # the limit price of the customer order
        self.quantity = qty        # the quantity to buy/sell

    def __str__(self):
        return 'Customer Order [T=%5.2f %s %s P=%s Q=%s]' % (self.time, self.trader_id, self.otype, self.price, 
            self.quantity)


# An order created by a trader for the exchange.
class Order:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES):
        self.id = -1                    # order i.d. (unique to each order on the Exchange)
        self.time = time                # timestamp
        self.trader_id = trader_id      # trader i.d.
        self.otype = otype              # order type
        self.quantity = quantity        # the original quantity of the order
        self.limit_price = limit_price  # limit price, None means no limit price
        self.MES = MES                  # minimum execution size, None means no MES
        self.BDS = False
        self.BDS_match_id = None
        self.quantity_remaining = quantity # the remaining on the order

    def __str__(self):
        return 'Order: [ID=%d T=%5.2f %s %s Q=%s QR=%s P=%s MES=%s]' % (self.id, self.time, self.trader_id, self.otype, 
            self.quantity, self.quantity_remaining, self.limit_price, self.MES)


# A block indication created by a trader for the exchange
class Block_Indication:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES

    def __str__(self):
        return 'BI: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s]' % (self.id, self.time, self.trader_id, 
            self.otype, self.quantity, self.limit_price, self.MES)


# An Order Submission Request (OSR) sent to a trader when their block indication is matched
class Order_Submission_Request:

    def __init__(self, OSR_id, time, trader_id, otype, quantity, limit_price, MES, match_id, reputational_score):
        self.id = OSR_id
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES
        self.match_id = match_id
        self.reputational_score = reputational_score

    def __str__(self):
        return 'OSR: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s MID=%d CRP=%s]' % (self.id, self.time, self.trader_id, 
            self.otype, self.quantity, self.limit_price, self.MES, self.match_id, self.reputational_score)


# A Qualifying Block Order (QBO) created by a trader for the exchange
class Qualifying_Block_Order:

    def __init__(self, time, trader_id, otype, quantity, limit_price, MES, match_id):
        self.id = -1
        self.time = time
        self.trader_id = trader_id
        self.otype = otype
        self.quantity = quantity
        self.limit_price = limit_price
        self.MES = MES
        self.match_id = match_id

    def __str__(self):
        return 'QBO: [ID=%d T=%5.2f %s %s Q=%s P=%s MES=%s MID=%d]' % (self.id, self.time, self.trader_id, self.otype, self.quantity, self.limit_price, self.MES, self.match_id)