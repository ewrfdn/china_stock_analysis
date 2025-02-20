import json
import re
import asyncio
import os
from datetime import datetime
from collectors.stock_base_info_collector import StockBaseInfoCollector

def get_urls(page_num: int):
    urls = []
    for i in range(1, page_num + 1):
        url = f"https://data.10jqka.com.cn/funds/ggzjl/field/zdf/order/desc/page/{i}/ajax/1/free/1/"
        urls.append(url)
    return urls
async def main():
    # List the URLs to fetch (modify as needed)
    urls = [
        "https://data.10jqka.com.cn/funds/ggzjl/field/zdf/order/desc/page/2/ajax/1/free/1/",
    ]
    try:
        async with StockBaseInfoCollector() as sc:
            for url in get_urls(103):
                await sc.collect_data(url)
            await sc.collect_history_data()
            sc.export_to_excel()
    except Exception as e:
        raise e
    

if __name__ == "__main__":
    asyncio.run(main())
