import httpx
import logging

from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logging.warning("DrWeb is slow, inaccurate and may throw unexpected errors due to lack of testing")

class DrwebClient:
    def __init__(self, user_agent: str = "", timeouts: list = [30,30,30]):
        self.user_agent = user_agent
        self.timeout = httpx.Timeout(timeouts[0], connect=timeouts[1], read=timeouts[2])
        self.endpoint = "https://vms.drweb.com/online-check-result/?lng=en&uro=1&url=%s"
        self.client = httpx.Client(timeout=self.timeout)
        self.cache = {}
        self.result = {}

    def close_client(self) -> None:
        self.client.close()

    def new_client(self) -> None:
        self.client = httpx.Client()

    def clear_cache(self) -> None:
        self.cache.clear()

    def get_from_cache(self, url: str) -> dict | None:
        return self.cache.get(url, None)

    def get_cache(self) -> dict:
        return self.cache.copy()

    def _build_url(self, url: str) -> str:
        return self.endpoint % url

    @staticmethod
    def _process_data(data: dict) -> dict:
        html_content = data.get("text")
        tree = html.fromstring(html_content)

        site_clear = tree.xpath('//span[@class="site_clear"]/text()')[0]
        black_list = tree.xpath('//span[@class="black_list"]/text()')[0]

        redirect_urls = []
        report_section = tree.xpath('//div[@class="report"]')[0]
        for p in report_section.xpath('.//p'):
            if 'redirects to' in p.text_content():
                urls = p.xpath('.//b/text()')
                redirect_urls.extend(url.strip() for url in urls if url.strip())

        if site_clear != "No viruses":
            malicious = True
        elif black_list == "The website is not the in the Doctor Web malicious sites database":
            malicious = True
        else:
            malicious = False
        return {
            "error": None,
            "malicious": malicious,
            "redirect": True if len(redirect_urls) > 0 else False,
            "redirect_urls": redirect_urls,
        }

    def gather_data(self, url: str) -> dict:
        target = self._build_url(url)
        headers = {"User-Agent": self.user_agent}

        if url in self.cache:
            return self.cache[url]

        try:
            response = self.client.get(target, headers=headers)
            response.raise_for_status()
            self.result = self._process_data(response.json())

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            self.result.update({"error": str(e)})
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.result.update({"error": str(e)})

        self.cache[url] = self.result
        return {"drweb":self.result}