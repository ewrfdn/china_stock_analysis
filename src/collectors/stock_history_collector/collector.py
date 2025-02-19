import json
import shutil
import asyncio
import os
from os import path
from utils.request_tool import RequestTool
from .parser import normalize_data, stock_KDJ_calculate, extra_json_data


class StockHistoryCollector():
    def __init__(self, root_path, force=False, type='daily'):
        self.root_folder = root_path
        self.type = type
        self.data_folder = path.join(self.root_folder, self.type)
        self.type_flag='01'
        if type == 'weekly':
            self.type_flag = '11'
        elif type == 'monthly':
            self.type_flag = '21'
        self.temp_file_path = path.join(self.data_folder, 'temp.json')
        self.save_count = 0
        self.max_save_count = 10
        self.temp_data = {
            "succeed_stocks": []}
        self.force = force
        self.init()
        self.request_tool = RequestTool()

    async def __aenter__(self):
        if self.force:
            self.clean()
        self.init()
        return self
        
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
    
    async def close(self):
        self.save_count = self.save_count + 1
        self.auto_save()
        await self.request_tool.closeSession()

    def clean(self):
        # remve current data folder
        shutil.rmtree(self.data_folder)

    def init(self):
        # ensure dir
        if not path.exists(self.root_folder):
            os.mkdir(self.root_folder)

        if not path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        if path.exists(self.temp_file_path):
            try:
                with open(self.temp_file_path, 'r', encoding='utf-8') as f:
                    self.temp_data = json.load(f)
            except json.decoder.JSONDecodeError:
                self.temp_data = {
                    "succeed_stocks": [],
                }

    def auto_save(self):
        self.save_count = self.save_count + 1
        if self.save_count % self.max_save_count == 0:
            self.save_count = 0
            with open(self.temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.temp_data, f,ensure_ascii=False, indent=4)




    async def collect_data(self, stock_code):
        url=f'https://d.10jqka.com.cn/v6/line/hs_{stock_code}/{self.type_flag}/all.js'
        today_url = f'https://d.10jqka.com.cn/v6/line/hs_{stock_code}/{self.type_flag}/defer/today.js'
        if stock_code in self.temp_data['succeed_stocks']:
            with open(path.join(self.data_folder, stock_code+'.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        json_data = await self.request_tool.afetch_with_browser(url)
        if json_data is None:
            return
        today_data = await self.request_tool.afetch_with_browser(today_url)
        if today_data is None:
            return
        normalized_data = normalize_data(json_data)
        today_data = extra_json_data(today_data)
        today_data = today_data['hs_'+stock_code]
        normalized_data['short_date'] = today_data['1']
        short_date = today_data['1'][-4:]
        if normalized_data['data'][-1]['date'] != short_date:
            normalized_data['data'].append({
                "date": short_date,
                'final_price': int(float(today_data['11'])*100),
                "low_price": int(float(today_data['9'])*100),
                "high_price": int(float(today_data['8'])*100),
                "start_price": int(float(today_data['7'])*100),
            })
        
        final_data = stock_KDJ_calculate(normalized_data)
        with open(path.join(self.data_folder, stock_code+'.json'), 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        self.temp_data['succeed_stocks'].append(stock_code)
        self.auto_save()
        return final_data