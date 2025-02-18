TABLE_MAPPING = {
    "股票代码": "stock_code",
    "股票简称": "stock_name",
    "最新价": "latest_price",
    "涨跌幅": "change_percent",
    "换手率": "turnover_rate",
    "流入资金(元)": "inflow",
    "流出资金(元)": "outflow",
    "净额(元)": "net",
    "成交额(元)": "transaction_amount",
}

def mapping_keys(map, mapping):
    new_map = {}
    for (key, value) in map.items():
        if key in mapping:
            new_map[mapping[key]] = {
                **value,
                "title": key,
            }
        else:
            new_map[key] = {
                **value,
                "title": key,
            }
    return new_map