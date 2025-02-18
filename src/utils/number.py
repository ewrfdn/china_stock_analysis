import re

def convert_to_wan(text):
    """
    将含有 '亿' 单位的数值转换为万为单位（返回浮点数），
    如果包含 '万' 则移除单位并转换为浮点数，
    非 '亿' 和 '万' 的文本返回原始值。
    例如:
        '12.91亿' -> 129100.0
        '8641.20万' -> 8641.20
    """
    if not isinstance(text, str):
        return text
    if "亿" in text:
        try:
            num = float(text.replace("亿", "").strip())
            return num * 10000
        except ValueError:
            return text
    elif "万" in text:
        try:
            num = float(text.replace("万", "").strip())
            return num
        except ValueError:
            return text
    elif text =='0.00':
        return 0.00
    return text

def parse_percent(text):
    if isinstance(text, (str)):
        match = re.search(r'[-+]?\d*\.?\d+%', text)
        if match:
            try:
                return float(match.group().replace('%', ''))
            except ValueError:
                return text
    return text

def convert_value(text):
    value = parse_percent(text)
    value = convert_to_wan(value)
    return value

def parse_number(text):
    match = re.search(r'[-+]?\d*\.?\d+', text.replace(',', ''))
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

def determine_color(text):
    value = parse_number(text)
    if value is None:
        return "FF000000"  # 黑色
    if value > 0:
        return "FFFF0000"  # 红色
    elif value < 0:
        return "FF00FF00"  # 绿色
    return "FF000000"