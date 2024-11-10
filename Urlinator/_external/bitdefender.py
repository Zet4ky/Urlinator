import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitdefenderClient:
    def __init__(self, user_agent: str = "", timeouts: list = [30, 30, 30]):
        self.user_agent = user_agent
        self.timeout = httpx.Timeout(timeouts[0], connect=timeouts[1], read=timeouts[2])
        self.endpoint = "https://nimbus.bitdefender.net/url/status?url=%s"
        self.client = httpx.Client()
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
        malicious = data.get("status_code", None) == 1
        threat_type = data.get("status_message", "unknown")
        categories = data.get("categories", [])

        return {
            "error": None,
            "malicious": malicious,
            "type": threat_type,
            "categories": categories
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
        return {"bitdefender":self.result}