
import asyncio
import json
from datetime import datetime
from pathlib import Path
from collectors.stock_company_info_collector import StockCompanyInfoCollector

async def main():
    # 读取JSON文件
    json_path = Path('data/2025-02-18/result.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取股票代码
    stock_codes = [stock['stock_code']['value'] for stock in data]
    
    async with StockCompanyInfoCollector(root_path='data') as collector:
        await collector.collect_batch(stock_codes, concurrency=2)
        collector.export_concepts()
        
    
    
if __name__ == '__main__':
    asyncio.run(main())
