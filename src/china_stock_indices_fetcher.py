from lxml import html

async def fetch_china_stock_indices(request_tool):
    # Use the supplied RequestTool instance to fetch HTML
    url = "https://quote.eastmoney.com/center/hszs.html"
    html_content = await request_tool.afetch_with_browser(url)
    if not html_content:
        raise ValueError("Failed to retrieve HTML content from the URL.")
    # Parse HTML and extract the target table using the specified XPath
    doc = html.fromstring(html_content)
    table_list = doc.xpath('//*[@id="mainc"]/div/div/table[1]')
    if not table_list:
        raise ValueError("Table not found using specified XPath.")
    return table_list[0]

# ...existing or additional utility functions if necessary...
