from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

def extra_json_data(data):
    if "<html>" in data:
        # 使用BS4解析HTML
        soup = BeautifulSoup(data, 'html.parser')
        pre_tag = soup.select_one('pre')
        if pre_tag:
            data = pre_tag.text
    
    # Match any function name followed by parentheses content
    pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)')
    result = pattern.match(data)
    if result:
        try:
            return json.loads(result.group(2))
        except json.JSONDecodeError:
            return None
    return None

def normalize_data(data):
    json_data = extra_json_data(data)
    result = {
        'cur_price': None,
        'data': [],
        "full_date": datetime.now().strftime("%Y-%m-%d:%H:%M:%S"),
        'name': ''
    }
    try:
        prices = json_data['price'].split(',')
        dates = json_data['dates'].split(',')
        volume = json_data['volumn'].split(',')
        name = json_data['name']
        result['name'] = name
        step = len(prices) // len(dates)
        for i in range(0, len(prices), step):
            date_index = i // step
            result['data'].append({
                'date': dates[date_index],
                'final_price': int(prices[i]) + int(prices[i+3]),
                "low_price": int(prices[i]),
                "high_price": int(prices[i]) + int(prices[i+2]),
                "start_price": int(prices[i]) + int(prices[i+1]),
                'volume': volume[date_index]
            })
        result['short_date'] = result['data'][-1]['date']
        result['cur_price'] = result['data'][-1]['final_price']
        result['delta'] = result['data'][-1]['final_price'] - result['data'][0]['final_price']
        if result['data'][0]['final_price'] != 0:
            result['delta_percent'] = result['delta'] / result['data'][0]['final_price']
    except json.JSONDecodeError:
        return None
    return result

def stock_KDJ_calculate(normalized_data, n=9):
    """
    计算KDJ指标
    normalized_data: 标准化后的数据
    n: RSV计算周期，默认为9
    """
    data = normalized_data['data']
    
    if len(data) < n:
        print(f"Warning: 数据量不足，需要至少 {n} 天的数据")
        return normalized_data
    
    # 初始化K、D值，默认为50
    k_prev = 50
    d_prev = 50
    
    for i in range(len(data)):
        data[i]['K'] = None
        data[i]['D'] = None
        data[i]['J'] = None
        
        if i >= n - 1:
            window_data = data[i-(n-1):i+1]
            # 将价格除以100获取实际价格
            highest_high = max(window_data, key=lambda x: x['high_price'])['high_price'] / 100
            lowest_low = min(window_data, key=lambda x: x['low_price'])['low_price'] / 100
            close_price = data[i]['final_price'] / 100
            
            # 计算RSV值
            if highest_high != lowest_low:
                rsv = (close_price - lowest_low) * 100 / (highest_high - lowest_low)
            else:
                rsv = 0
            
            # 计算KDJ指标
            k_value = (2/3 * k_prev + 1/3 * rsv)
            d_value = (2/3 * d_prev + 1/3 * k_value)
            j_value = 3 * k_value - 2 * d_value
            
            # 存储计算结果
            data[i]['K'] = k_value
            data[i]['D'] = d_value
            data[i]['J'] = j_value
            
            k_prev = k_value
            d_prev = d_value
    return normalized_data