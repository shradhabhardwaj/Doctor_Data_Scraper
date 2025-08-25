# url_scraper/scrapers/selenium_base_scraper.py

import asyncio
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Corrected import path relative to the url_scraper directory
from ..utils.logger import app_logger

class SeleniumBaseScraper(ABC):
    """
    Abstract base class for scrapers requiring JavaScript rendering.
    It manages a Selenium WebDriver instance and fetches dynamic content
    in a way that is compatible with an asyncio event loop.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        app_logger.info("Selenium WebDriver initialized in headless mode.")

    """
    def _get_page_source_sync(self, url: str) -> str | None:
        
        #[Synchronous] Helper method that performs the actual browser actions.
        #This function will be run in a separate thread to avoid blocking asyncio.
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.listing-doctor-card"))
            )
            return self.driver.page_source
        except Exception as e:
            app_logger.error(f"Selenium failed to fetch or wait for content at {url}. Error: {e}")
            return None
        """
    # ... (imports and other class methods are unchanged) ...

    def _get_page_source_sync(self, url: str) -> str | None:
        """
        [Synchronous] Helper method that performs the actual browser actions.
        This function will be run in a separate thread to avoid blocking asyncio.
        """
        try:
            self.driver.get(url)
            # Wait for up to 10 seconds for the main doctor card container to be visible.
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.listing-doctor-card"))
            )
            return self.driver.page_source
        except Exception as e:
            # This is now an INFO log, as a timeout is the expected way to find the last page.
            app_logger.info(f"Timeout waiting for doctor cards on {url}. Assuming this is the last page.")
            return None

    # ... (the rest of the file is unchanged) ...


    async def fetch_with_browser(self, url: str) -> str | None:
        """
        [Asynchronous] Fetches a URL using the Selenium WebDriver by running it in a thread.
        """
        loop = asyncio.get_running_loop()
        html_content = await loop.run_in_executor(None, self._get_page_source_sync, url)
        return html_content

    @abstractmethod
    async def scrape(self, specialty: str) -> list[dict]:
        pass

    def close_session(self):
        """Closes the Selenium WebDriver session."""
        if self.driver:
            self.driver.quit()
            app_logger.info("Selenium WebDriver session closed.")