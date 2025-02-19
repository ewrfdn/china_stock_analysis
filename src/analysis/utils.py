def sort_stocks(stock_list, sort_key, reverse=False, cutoff=None, comparison_type='>='):
    """
    Sort stock data by specified key and filter by cutoff value
    
    Args:
        stock_list (list): List of stock dictionaries
        sort_key (str): Key to sort by (e.g., 'latest_price', 'change_percent')
        reverse (bool): True for descending order, False for ascending
        cutoff (float, optional): Value to filter results. Defaults to None.
        comparison_type (str): Type of comparison ('>=', '<='). Defaults to '>='.
        
    Returns:
        list: Sorted and filtered list of stock dictionaries
    """
    sorted_stocks = sorted(
        stock_list,
        key=lambda x: float(x[sort_key]['value']) if isinstance(x[sort_key]['value'], str) else x[sort_key]['value'],
        reverse=reverse
    )
    
    if cutoff is not None:
        if comparison_type == '>=':
            return [stock for stock in sorted_stocks 
                   if (float(stock[sort_key]['value']) if isinstance(stock[sort_key]['value'], str) 
                   else stock[sort_key]['value']) >= cutoff]
        elif comparison_type == '<=':
            return [stock for stock in sorted_stocks 
                   if (float(stock[sort_key]['value']) if isinstance(stock[sort_key]['value'], str) 
                   else stock[sort_key]['value']) <= cutoff]
    
    return sorted_stocks

# Usage examples:
# Get stocks with change_percent >= 10%
# filtered_stocks = sort_stocks(stock_list, 'change_percent', reverse=True, cutoff=10)
# Get stocks with price <= 50
# filtered_stocks = sort_stocks(stock_list, 'latest_price', reverse=False, cutoff=50, comparison_type='<=')

def stock_set_operation(list1, list2, key, operation='intersection'):
    """
    Perform set operations on two lists of stocks based on a specific key
    
    Args:
        list1 (list): First list of stock dictionaries
        list2 (list): Second list of stock dictionaries
        key (str): Key to use for comparison (e.g., 'stock_code')
        operation (str): Set operation to perform ('intersection', 'difference', 'union')
        
    Returns:
        list: Result of the set operation
    """
    # Convert values to comparable format
    set1 = {stock[key]['value'] for stock in list1}
    set2 = {stock[key]['value'] for stock in list2}
    
    # Perform set operation
    if operation == 'intersection':
        result_set = set1.intersection(set2)
    elif operation == 'difference':
        result_set = set1.difference(set2)
    elif operation == 'union':
        result_set = set1.union(set2)
    else:
        raise ValueError("Invalid operation. Use 'intersection', 'difference', or 'union'")
    
    # Return stocks from list1 that match the result
    return [stock for stock in list1 if stock[key]['value'] in result_set]

# Usage examples:
# Get common stocks between two lists
# common_stocks = stock_set_operation(list1, list2, 'stock_code', 'intersection')
# Get stocks in list1 but not in list2
# diff_stocks = stock_set_operation(list1, list2, 'stock_code', 'difference')
# Get all unique stocks from both lists
# all_stocks = stock_set_operation(list1, list2, 'stock_code', 'union')
