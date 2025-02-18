from utils.request_tool import RequestTool  # adjust import as needed
from headers import STOCK_LIST_HEADER
from datetime import datetime, timedelta
import os.path as path
import os
import shutil
from utils.write_to_excel import *
import json
from .parser import *
from collectors.stock_daily_collector import StockDailyCollector

class StockBaseInfoCollector:
    def __init__(self, root_folder='data', force = False):
        '''
        result example 

        '''
        self.result = []
        self.stock_info = {}
        self.list_rt = RequestTool(default_headers=STOCK_LIST_HEADER)
        self.info_rt = RequestTool(default_headers=STOCK_LIST_HEADER)
        self.root_folder = root_folder
        self.date_string = self.get_date_string()
        self.data_folder = path.join(self.root_folder, self.date_string)
        self.stock_info_file_path=path.join(self.data_folder, 'stock_info.json')
        self.result_file_path=path.join(self.data_folder, 'result.json') 
        self.temp_file_path=path.join(self.data_folder, 'temp.json')
        self.temp_data = {
             "succeed_urls": [],
             "succeed_stocks": [],
        }
        self.force = force
        self.daily_collector = StockDailyCollector(self.data_folder, self.force)
        self.daily_summary_file = path.join(self.root_folder, 'daily_summary.json')
        
    async def __aenter__(self):
        if self.force:
            self.clean()
        self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        self.auto_save()
        self.finalize_summary()
        await self.daily_collector.close()
        await self.list_rt.closeSession(),
        await self.info_rt.closeSession()

    @property
    def succeed_urls(self):
        return self.temp_data['succeed_urls']

    @property
    def succeed_stocks(self):
        return self.temp_data['succeed_stocks']

    def clean(self):
        # remve current data folder
        shutil.rmtree(self.data_folder)

    def init(self):
        # ensure dir
        if not path.exists(self.root_folder):
            os.mkdir(self.root_folder)

        if not path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        # Read daily summary file
        if path.exists(self.daily_summary_file):
            try:
                with open(self.daily_summary_file, 'r', encoding='utf-8') as f:
                    self.daily_summary = json.load(f)
            except json.decoder.JSONDecodeError:
                self.daily_summary = {}
        else:
            self.daily_summary = {}
        # create new file
        if path.exists(self.stock_info_file_path):
            try:
                with open(self.stock_info_file_path, 'r', encoding='utf-8') as f:
                    self.stock_info = json.load(f)
            except json.decoder.JSONDecodeError:
                self.stock_info = {}
        if path.exists(self.result_file_path):
            try:
                with open(self.result_file_path, 'r', encoding='utf-8') as f:
                    self.result = json.load(f)
            except json.decoder.JSONDecodeError:
                self.result = []
        if path.exists(self.temp_file_path):
            try:
                with open(self.temp_file_path, 'r', encoding='utf-8') as f:
                    self.temp_data = json.load(f)
            except json.decoder.JSONDecodeError:
                self.temp_data = {
                    "succeed_urls": [],
                    "succeed_stocks": [],
                }

    def auto_save(self):
        with open(self.stock_info_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.stock_info, f,ensure_ascii=False, indent=4)
        with open(self.result_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.result, f,ensure_ascii=False, indent=4)
        with open(self.temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.temp_data, f,ensure_ascii=False, indent=4)
    
    def get_date_string(self):
        now = datetime.now()
        cutoff = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if now < cutoff:
            new_date = now - timedelta(days=1)
        else:
            new_date = now
        return new_date.strftime("%Y-%m-%d")

    # 根据股票代码，返回self.
    def unique_data(self, list):
        pass

    # 传入url 获取 收集股票信息的入口文件，根据url 先拿到股票信息的列表，
    # 在根据股票信息列表获取到的url 哪去股票的详细信息并分类合并
    # 每一次collect data后应该在文件夹下保存当前信息
    async def collect_data(self, url):
        try:
            if url in self.succeed_urls:
                print(f"{url} already fetched skip")
                return
            html = await self.list_rt.afetch_with_browser(url)
            if html:
                new_result = process_stock_list_html(html)
                for item in new_result:
                    stock_code = item.get('stock_code').get('value')
                    stock_info = await self.daily_collector.collect_data(stock_code)
                    if stock_info:
                        item.update({
                            "final_price":{
                                "value": stock_info['cur_price'],
                                "title": "收盘价格",
                            },
                            "D":{ "value": stock_info['data'][-1]['D'], "title": "D值"},
                            "K":{ "value": stock_info['data'][-1]['K'], "title": "K值"},
                            "J":{ "value": stock_info['data'][-1]['J'], "title": "J值"},
                        })
                self.result.extend(new_result)
            self.succeed_urls.append(url)
            self.auto_save()
        except Exception as e:
            print(f"failed to fetch {url}: {e}")

    def export_to_excel(self):
        write_to_excel(self.result, f'{self.data_folder}/result.xlsx')
    
    # 根据第一步获取到的股票信息，爬取股票信息的相信网页，补全result中每一项的
    async def collect_all_stock_info(self):
        pass

    def finalize_summary(self):
        total_transaction_amount = 0
        total_inflow = 0
        total_outflow = 0
        total_net = 0
        for stock in self.result:
            total_transaction_amount += float(stock.get('transaction_amount', {}).get('value', 0))
            total_inflow += float(stock.get('inflow', {}).get('value', 0))
            total_outflow += float(stock.get('outflow', {}).get('value', 0))
            total_net += float(stock.get('net', {}).get('value', 0))
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_summary[today] = {
            "transaction_amount": {
                "value": total_transaction_amount,
                "title": "成交额(元)"
            },
            "inflow": {
                "value": total_inflow,
                "title": "流入资金(元)"
            },
            "outflow": {
                "value": total_outflow,
                "title": "流出资金(元)"
            },
            "net": {
                "value": total_net,
                "title": "净额(元)"
            }
        }
        with open(self.daily_summary_file, 'w', encoding='utf-8',) as f:
            json.dump(self.daily_summary, f, indent=4,ensure_ascii=False)
        self.export_summary_to_excel()

    def export_summary_to_excel(self):
        rows = []
        # Each row is in the same format as the JSON, with an extra 'date' key.
        for date, summary in self.daily_summary.items():
            row = {"date": {
                "value": date,
                "title": "日期"
            }}
            row.update(summary)
            print(row)
            rows.append(row)
        excel_path = path.join(self.root_folder, 'daily_summary.xlsx')
        write_to_excel(rows, excel_path)

