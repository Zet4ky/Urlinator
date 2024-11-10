import httpx
import logging

import base64
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Todo: Help
"""

class KasperskyClient:
    def __init__(self, user_agent: str = "", timeouts: list = [30, 30, 30]):
        self.user_agent = user_agent
        self.timeout = httpx.Timeout(timeouts[0], connect=timeouts[1], read=timeouts[2])
        self.endpoint = "https://opentip.kaspersky.com/ui/lookup"
        self.session_ep = "https://opentip.kaspersky.com/ui/checksession"
        self.client = httpx.Client(timeout=self.timeout)
        self.cache = {}
        self.result = {}
        self.renew_session_date = None
        self.api_key = None

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

    @staticmethod
    def _build_url(url: str) -> str:
        return url

    def _get_session(self) -> None:
        # Todo: Clean up this.
        session_response = self.client.get(self.session_ep)
        session_response.raise_for_status()
        self.api_key = session_response.headers.get("cym9cgwjk", None)
        decoded_api_key = str(base64.b64decode(self.api_key))
        json_like_string = decoded_api_key[decoded_api_key.find("{"):decoded_api_key.rfind("}") + 1]
        deadline_key = '"deadline":'
        deadline_start = json_like_string.find(deadline_key) + len(deadline_key)
        deadline_end = json_like_string.find(",", deadline_start)
        deadline = json_like_string[deadline_start:deadline_end].strip().strip('"')
        self.renew_session_date = int(deadline) - 1000

    def _check_session(self) -> None:
        current_date = int(datetime.now().timestamp() * 1000)
        if self.api_key is None:
            self._get_session()

        if current_date >= self.renew_session_date:
            self._get_session()

    @staticmethod
    def _process_data(data: dict) -> dict:
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
        if url in self.cache:
            return self.cache[url]

        self._check_session()
        target = self._build_url(url)
        headers = {"User-Agent": self.user_agent, "cym9cgwjk": self.api_key}

        try:
            body = {"query": target, "silent": True}
            response = self.client.post(self.endpoint,headers=headers, json=body)
            response.raise_for_status()
            print(response.json())
            self.result = self._process_data(response.json())

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            self.result.update({"error": str(e)})
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.result.update({"error": str(e)})

        self.cache[url] = self.result
        return {"kaspersky": self.result}
