from bs4 import BeautifulSoup
from utils.number import convert_value, determine_color
from utils.mapping import TABLE_MAPPING, mapping_keys

def process_stock_list_html(html):
    print('process_stock_list_html:--------',html)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    headers = []
    header_row = table.find('thead').find('tr')
    for th in header_row.find_all('th'):
        header_text = th.get_text(strip=True)
        if header_text == "序号":  # skip index column
            continue
        headers.append(header_text)
    
    data = []
    for tr in table.find('tbody').find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) < len(headers)+1:
            continue
        row = {}
        # Skip first td (序号) and iterate rest
        for idx, header in enumerate(headers, start=1):
            extenal = {}
            cell = tds[idx]
            cell_text = cell.get_text(strip=True)
            if header == "股票代码":
                a_tag = cell.find('a')
                extenal['href'] = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
                cell_value = cell.get_text(strip=True)
            else:
                cell_value = cell_text
            # 对指定字段使用 determine_color，否则使用默认 aRGB 黑色 "FF000000"
            if any(keyword in header for keyword in ["涨跌幅", "流出资金", "流入资金", "净额"]):
                extenal['textColor'] = determine_color(cell_text)
            row[header] = {
                "value": convert_value(cell_value),
                **extenal,
            }
        data.append(mapping_keys(row, TABLE_MAPPING))
    return data
