from analysis.stock_simulation import StockSimulation
from analysis.selection import select_random_high_turnover,select_random_stock

def run():
    file_list = [
        'data/2025-02-10/result.json',
        'data/2025-02-11/result.json',
        'data/2025-02-12/result.json',
        'data/2025-02-13/result.json',
        'data/2025-02-17/result.json',
        'data/2025-02-18/result.json',
        'data/2025-02-19/result.json',
    ]
    initial_investment = 50000
    total_cash = 0
    ## 存放赚钱的次数
    profit_count = 0
    ## 存放赔钱的次数
    loss_count = 0
    simulation = StockSimulation(file_list, select_random_high_turnover, initial_investment)
    # 进行1000次模拟
    simulate_times = 1000
    for i in range(simulate_times):
        result = initial_investment
        simulation.reset()
        while True:
            temp = simulation.next()
            
            if temp is None:
                break
            else:
                result = temp
            print(result)
        total_cash += result
        if result > initial_investment:
            profit_count += 1
        else:
            loss_count += 1
    # 平均收益
    average_profit = (total_cash - initial_investment * simulate_times) / 1000
    print(f"总收益: {total_cash - initial_investment * simulate_times}")
    print(f"赚钱的次数: {profit_count}")
    print(f"赔钱的次数: {loss_count}")
    print(f"平均收益: {average_profit}")
        


run()

