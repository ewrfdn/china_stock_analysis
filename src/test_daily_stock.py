import asyncio
from collectors.stock_history_collector import StockDailyCollector

async def main():
    async with StockDailyCollector('./data') as sc:
        result = await sc.collect_data('002594')
        print(result['name'])

if __name__ == "__main__":
    asyncio.run(main())