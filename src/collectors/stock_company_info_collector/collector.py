import json
import os
from os import path
import asyncio
from bs4 import BeautifulSoup
from utils.request_tool import RequestTool
from utils.async_utils import async_run_all  # Add this import

class StockCompanyInfoCollector:
    FIELD_MAPPING = {
        "所属地域": "region",
        "涉及概念": "concepts",
        "主营业务": "main_business",
        "上市日期": "listing_date",
        "每股净资产": "net_asset_per_share",
        "每股收益": "earnings_per_share",
        "净利润": "net_profit",
        "净利润增长率": "net_profit_growth",
        "营业收入": "revenue",
        "每股现金流": "cash_flow_per_share",
        "每股公积金": "capital_reserve_per_share",
        "每股未分配利润": "undistributed_profit_per_share",
        "总股本": "total_shares",
        "流通股": "floating_shares"
    }

    def __init__(self, root_path, force=False):
        self.root_folder = root_path
        self.data_folder = path.join(self.root_folder, 'company_details')
        self.data_file_path = path.join(self.data_folder, 'company_details.json')
        self.save_count = 0
        self.max_save_count = 10
        self.company_data_list = []
        self.force = force
        self.request_tool = RequestTool(debug=True)
        self.concepts_file_path = path.join(self.data_folder, 'concepts.json')
        self.init()

    def clean(self):
        if path.exists(self.data_file_path):
            os.remove(self.data_file_path)

    def init(self):
        if not path.exists(self.root_folder):
            os.mkdir(self.root_folder)
        if not path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        if path.exists(self.data_file_path):
            try:
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self.company_data_list = json.load(f)
            except json.decoder.JSONDecodeError:
                self.company_data_list = {
                    "succeed_stocks": [],
                    "details": {}
                }

    def auto_save(self):
        self.save_count = self.save_count + 1
        if self.save_count % self.max_save_count == 0:
            self.save_count = 0
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.company_data_list, f, ensure_ascii=False, indent=4)

    def _parse_company_details(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        company_details = soup.find('dl', class_='company_details')
        if not company_details:
            return None

        result = {}
        current_key = None
        
        for element in company_details.children:
            if element.name == 'dt':
                current_key = element.text.replace('：', '').strip()
            elif element.name == 'dd' and current_key:
                # Skip if no English mapping exists
                if current_key not in self.FIELD_MAPPING:
                    continue
                    
                eng_key = self.FIELD_MAPPING[current_key]
                
                # Handle special case for main_business
                if current_key == '主营业务':
                    if 'title' in element.attrs:
                        result[eng_key] = {
                            "value": element['title'],
                            "type": "string",
                            "title": current_key
                        }
                    continue
                
                value = element.text.strip()
                if current_key in ['每股净资产', '每股收益', '每股现金流', '每股公积金', '每股未分配利润']:
                    value = float(value.replace('元', ''))
                    value_type = "float"
                elif current_key in ['净利润增长率']:
                    value = float(value.replace('%', ''))
                    value_type = "percentage"
                elif current_key in ['总股本', '流通股']:
                    value = float(value.replace('亿', '')) * 10000
                    value_type = "int"
                elif current_key in ['净利润', '营业收入']:
                    value = float(value.replace('亿元', '')) * 10000
                    value_type = "int"
                elif current_key == '涉及概念':
                    value = element['title'].split('，') if 'title' in element.attrs else value.split('，')
                    value_type = "array"
                else:
                    value_type = "string"
                
                result[eng_key] = {
                    "value": value,
                    "type": value_type,
                    "title": current_key
                }

        return result

    async def collect_data(self, stock_code):
        try:
            exist_company_data = list(filter(lambda x: x['stock_code']['value'] == stock_code, self.company_data_list))
            if exist_company_data:
                return exist_company_data[0]

            url = f'https://stockpage.10jqka.com.cn/{stock_code}/'
            html_content = await self.request_tool.afetch_with_browser(url)
            if html_content:
                company_data = self._parse_company_details(html_content)
                
                if company_data:
                    company_data['stock_code'] = {
                    "value": stock_code,
                    "type": "string",
                    "title": "股票代码"
                    }
                    self.company_data_list.append(company_data)
                    self.auto_save()
                    return company_data
        except Exception as e:
            print(f"Failed to collect data for stock code: {stock_code} e: {e}")
        print(f"Failed to collect data for url: {url}")
        return None

    async def collect_batch(self, stock_codes, concurrency=5):
        """
        Batch collect company details for multiple stock codes
        
        Args:
            stock_codes (list): List of stock codes to collect
            concurrency (int): Number of concurrent requests. Defaults to 5.
            
        Returns:
            list: List of collected company details
        """
        # Convert to list of single-item tuples for async_run_all
        params_list = [(code,) for code in stock_codes]
        results = await async_run_all(self.collect_data, params_list, concurrency)
        # Filter out None results
        return [r for r in results if r is not None]

    def export_concepts(self):
        """
        Export all unique concepts from company data to a JSON file.
        The exported data includes:
        - all_concepts: list of all unique concepts
        - concept_details: dictionary with concept as key and related companies as value
        """
        all_concepts = set()
        concept_details = {}

        # Collect all concepts and their related companies
        for company in self.company_data_list:
            if 'concepts' in company and company['concepts']['value']:
                stock_code = company['stock_code']['value']
                concepts = company['concepts']['value']
                
                for concept in concepts:
                    all_concepts.add(concept)
                    if concept not in concept_details:
                        concept_details[concept] = []
                    concept_details[concept].append(stock_code)

        # Convert to sorted list
        sorted_concepts = sorted(list(all_concepts))

        # Prepare export data
        export_data = {
            "all_concepts": sorted_concepts,
            "concept_details": concept_details,
            "total_concepts": len(sorted_concepts)
        }

        # Save to file
        with open(self.concepts_file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)

        return export_data

    async def __aenter__(self):
        if self.force:
            self.clean()
        self.init()
        return self
        
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
    
    async def close(self):
        self.auto_save()  # Final save before closing
        self.export_concepts()  # Export concepts before closing
        await self.request_tool.closeSession()
        await asyncio.sleep(1)  # Add a delay before closing

