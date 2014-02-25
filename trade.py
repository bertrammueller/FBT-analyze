import igcontrol as ig

class Trade():
    def __init__(self, trade_id, symbol, start, num_contracts, longshort, stop):
        self.trade_id = trade_id
        self.symbol = symbol
        self.start = start
        self.num_contracts = num_contracts
        self.stop = stop
        self.longshort = longshort
    
        ig.activate_firefox()
        ig.open_position(symbol, longshort, num_contracts, stop)
    
    def is_active(self):
        ig.activate_firefox()
        return ig.is_position_open(self.symbol)

    def close_position(self, num_contracts):
        ig.activate_firefox()
        if self.num_contracts <= 0:
            print 'This trade is terminated'
            return False
        if ig.close_position(self.symbol, self.longshort, num_contracts):
            self.num_contracts = self.num_contracts - num_contracts
            return True
        else:
            return False
    
    def change_stop(self, stop):
        ig.activate_firefox()
        if ig.change_stop(self.symbol, stop):
            self.stop = stop
            return True
        else:   
            return False
        