import aiohttp
import asyncio
from pyppeteer import launch  # headless browser via pyppeteer
import time
from utils.async_utils import run_async  # for synchronous launching of browser

class RequestTool:
    def __init__(self, cookies: dict = None, concurrency: int = 5, retries: int = 3, retry_delay: int = 1, default_headers: dict = None):
        self.concurrency = concurrency
        self.cookies = cookies
        self.retries = retries
        self.retry_delay = retry_delay
        self.semaphore = asyncio.Semaphore(concurrency)
        self.session = None
        self.default_headers = default_headers or {}
        # Launch headless browser at initialization using pyppeteer with Edge.
        self.browser = None
    
    def ensureSession(self):
        # 如果 session 不存在或已关闭则创建一个新的 session
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def closeSession(self):
        # 如果 session 存在且未关闭，则关闭它
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
        # Close the pre-initialized browser if it exists.
        if self.browser:
            await self.browser.close()
            self.browser = None

    async def afetch(self, url: str, method: str = 'get', headers: dict = None, params: dict = None) -> str:
        merge_headers = self.default_headers.copy()
        if headers:
            merge_headers.update(headers)
        self.ensureSession()
        for attempt in range(self.retries):
            async with self.semaphore:
                try:
                    async with self.session.request(method, url, headers=merge_headers, cookies=self.cookies, params=params) as response:
                        response.raise_for_status()
                        return await response.text()
                except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
                    print(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < self.retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    else:
                        raise e

    async def ensureBrowser(self):
        if self.browser is None:
            self.browser = await launch(headless=True, executablePath='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')

    async def afetch_with_browser(self, url: str, wait_time: int = 5) -> str:
        """
        Asynchronously fetch page content using a pre-initialized browser.
        Uses an installed Edge if executablePath is provided.
        """
        await self.ensureBrowser()
        page = await self.browser.newPage()
        try:
            # Set a common User-Agent string
            await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36")
            # Set additional HTTP headers to simulate a real browser request
            await page.setExtraHTTPHeaders({
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://data.10jqka.com.cn/",
            })
            # Stronger anti-headless detection code
            await page.evaluateOnNewDocument('''() => {
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                window.chrome = { runtime: {}, app: { isInstalled: false } };
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) =>
                  parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);
                const originalGetParameter = window.navigator.webdriver ? () => false : () => undefined;
                window.navigator.__proto__.getParameter = originalGetParameter;
            }''')
            await page.goto(url, {'waitUntil': 'networkidle2'})
            await page.waitFor(wait_time * 1000)
            content = await page.content()
            print(f"Fetched {url}")
            print(content)
            return content
        finally:
            await page.close()

    def fetch(self, url: str, method: str = 'get', headers: dict = None, params: dict = None) -> str:
        return asyncio.run(self.afetch(url, method, headers, params))
