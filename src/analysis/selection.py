import random
from .utils import sort_stocks

def select_by_turnover(data,cutoff=20,comparison_type='>='):
    return sort_stocks(data, 'turnover_rate', reverse=True, cutoff=cutoff, comparison_type=comparison_type)

def select_by_inflow(data,cutoff=0,comparison_type='>='):
    return sort_stocks(data, 'inflow', reverse=True, cutoff=cutoff, comparison_type=comparison_type)

def select_random_high_turnover(historical_stocks):
    if not historical_stocks:
        return None
    last_day_stocks = historical_stocks[-1]
    filtered = select_by_turnover(last_day_stocks)
    filtered = select_by_inflow(filtered)
    if not filtered:
        return None
    choice= random.choice(filtered)
    # print('选择的股票:', choice['stock_name']['value'],'换手率:', choice['turnover_rate']['value'])
    return choice

def select_random_stock(historical_stocks):
    if not historical_stocks:
        return None
    last_day_stocks = historical_stocks[-1]
    choice = random.choice(last_day_stocks)
    # print('选择的股票:', choice['stock_name']['value'])
    return choice
