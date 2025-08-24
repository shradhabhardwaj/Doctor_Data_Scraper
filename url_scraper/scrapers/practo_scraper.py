# url_scraper/scrapers/practo_scraper.py

from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from utils.logger import app_logger

class PractoScraper(BaseScraper):
    """Scraper for extracting doctor profile URLs from Practo.com."""

    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.name = "Practo"

    async def _parse_profile_links(self, html_content: str) -> list[str]:
        """
        Parses the HTML of a search results page to find profile links using
        the corrected 2025 selectors.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        links = set()
        
        # This selector for the main container is correct.
        doctor_cards = soup.find_all('div', class_='info-section')
        
        for card in doctor_cards:
            # CORRECTED LOGIC: The <a> tag is a parent of the <h2>.
            # We find the <a> tag first, then verify it contains the doctor name.
            link_tag = card.find('a')
            
            if link_tag and 'href' in link_tag.attrs:
                # This check ensures we only get the main profile link, not other random links.
                if link_tag.find('h2', {'data-qa-id': 'doctor_name'}):
                    full_url = "https://www.practo.com" + link_tag['href']
                    links.add(full_url)
                    
        return list(links)

    async def scrape(self, specialty: str) -> list[str]:
        """
        Scrapes all pages for a given specialty on Practo and returns
        a list of unique doctor profile URLs.
        """
        app_logger.info(f"Starting {self.name} scrape for specialty: {specialty}")
        all_urls = set()
        page = 1
        
        while True:
            search_url = f"{self.base_url}/{specialty}?page={page}"
            app_logger.debug(f"[{self.name}] Fetching page {page} for {specialty}: {search_url}")

            response = await self.fetch(search_url)
            if not response:
                app_logger.warning(f"[{self.name}] No response for page {page} of {specialty}. Stopping.")
                break

            profile_links = await self._parse_profile_links(response.text)
            
            if not profile_links:
                if page == 1:
                    app_logger.warning(f"[{self.name}] No profiles found on the FIRST page for {specialty}. This might indicate a selector change. Saving page HTML to 'debug_page.html' for analysis.")
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                
                app_logger.info(f"[{self.name}] No more profiles found for {specialty} on page {page}. Ending scrape for this specialty.")
                break
            
            new_links_found = len(set(profile_links) - all_urls)
            app_logger.info(f"[{self.name}] Found {len(profile_links)} links on page {page}. {new_links_found} are new.")
            
            all_urls.update(profile_links)
            page += 1
            
        app_logger.info(f"[{self.name}] Finished scraping for {specialty}. Found {len(all_urls)} total unique URLs.")
        return list(all_urls)