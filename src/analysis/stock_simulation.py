from functools import lru_cache


class StockSimulation:
    def __init__(self, file_list, selection_method, total_investment):
        self.file_list = file_list
        self.selection_method = selection_method
        self.total_investment = total_investment
        self.day_index = 0
        self.current_stock = None
        self.current_shares = 0
        self.total_investment = total_investment
        self.current_cash = total_investment
        self.transaction_history = []
        self.historical_stocks = []
    
    def reset(self):
        self.day_index = 0
        self.current_stock = None
        self.current_shares = 0
        self.current_cash = self.total_investment
        self.transaction_history = []

    def next(self):
        if self.day_index >= len(self.file_list):
            return None  # No more data
        
        file_path = self.file_list[self.day_index]
        current_day_stocks = self._load_stock_data(file_path)
        self.historical_stocks.append(current_day_stocks)
        
        if self.day_index == 0:
            budget = self.current_cash / 2
        else:
            budget = self.current_cash
        self.current_cash -= budget
        if budget < 0:
            return None
        shares_bought=0
        leftover=0
        # Call the user-provided selection method to pick a stock
        chosen_stock = self.selection_method(self.historical_stocks)
        if chosen_stock:
            chosen_price = self._get_stock_price(current_day_stocks, chosen_stock)
            if chosen_price:
                shares_bought, leftover = self._buy_stock(budget, chosen_price)
                if shares_bought > 0:
                    cost = shares_bought * chosen_price
                    self.current_cash += leftover
                    self.transaction_history.append({
                        'day': self.day_index,
                        'action': 'BUY',
                        'stock_code': chosen_stock['stock_code']['value'],
                        'price': chosen_price,
                        'shares': shares_bought,
                        'amount': cost
                    })

        if self.current_stock:
            self._sell_current_stock(current_day_stocks)
        if chosen_price and shares_bought > 0:
            self.current_shares = shares_bought
            self.current_stock = chosen_stock
        self.day_index += 1
        return self.current_cash + (self.current_shares * chosen_price)

    def get_trade_history(self):
        return self.transaction_history

    @lru_cache(maxsize=128)
    def _load_stock_data(self, file_path):
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data  # expects format similar to sort_stocks usage
    
    def _get_stock_price(self, stocks, target_stock):
        target_code = target_stock['stock_code']['value']
        for s in stocks:
            if s['stock_code']['value'] == target_code:
                return float(s['latest_price']['value'])
        return None

    def _sell_current_stock(self, current_day_stocks):
        sell_price = self._get_stock_price(current_day_stocks, self.current_stock)
        if sell_price:
            proceeds = self.current_shares * sell_price
            self.transaction_history.append({
                'day': self.day_index,
                'action': 'SELL',
                'stock_code': self.current_stock['stock_code']['value'],
                'price': sell_price,
                'shares': self.current_shares,
                'amount': proceeds
            })
            self.current_cash += proceeds
        self.current_stock = None
        self.current_shares = 0

    @staticmethod
    def _buy_stock(budget, price):
        if not price or budget < 100 * price:
            return 0, budget
        max_shares = int(budget // price)
        shares_to_buy = max_shares - (max_shares % 100)
        cost = shares_to_buy * price
        leftover = budget - cost
        return shares_to_buy, leftover