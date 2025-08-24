# scrapers/base_scraper.py : This abstract class is the engine. It handles all network operations, making child scrapers cleaner.


import asyncio
import random
from abc import ABC, abstractmethod
import httpx
from bs4 import BeautifulSoup

from utils.config import (
    RATE_LIMIT_SECONDS,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    REQUEST_TIMEOUT,
    USER_AGENTS,
    PROXY_LIST,
)
from utils.logger import app_logger

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers. It provides a robust infrastructure for
    making HTTP requests with sessions, retries, proxy/user-agent rotation,
    and rate limiting.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            proxy=self._get_proxy(),
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            http2=True  # Enable HTTP/2 for better performance on modern servers
        )

    def _get_proxy(self) -> dict | None:
        """Selects a random proxy if available."""
        if not PROXY_LIST:
            return None
        proxy = random.choice(PROXY_LIST)
        return {"http://": proxy, "https://": proxy}

    def _get_headers(self) -> dict:
        """Returns headers with a random user-agent."""
        return {"User-Agent": random.choice(USER_AGENTS)}

    async def fetch(self, url: str) -> httpx.Response | None:
        """
        Performs an asynchronous GET request with error handling and retries.
        """
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(RATE_LIMIT_SECONDS) # Rate limiting
                response = await self.client.get(url, headers=self._get_headers())
                response.raise_for_status() # Raise exception for 4xx/5xx responses
                return response
            
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                app_logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}. Error: {e}")
                if attempt + 1 == MAX_RETRIES:
                    app_logger.error(f"All retries failed for {url}. Giving up.")
                    return None
                
                # Exponential backoff
                backoff_delay = RATE_LIMIT_SECONDS * (BACKOFF_FACTOR ** attempt)
                await asyncio.sleep(backoff_delay)
        return None

    @abstractmethod
    async def scrape(self, specialty: str) -> list[str]:
        """
        Abstract method to be implemented by each specific scraper.
        It should orchestrate the scraping process for a given specialty
        and return a list of doctor profile URLs.
        """
        pass

    async def close_session(self):
        """Closes the httpx client session."""
        await self.client.aclose()