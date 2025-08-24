# main.py

import asyncio
import pandas as pd
from tqdm.asyncio import tqdm
import time

from scrapers.practo_scraper import PractoScraper
from scrapers.justdial_scraper import JustdialScraper
from utils.config import BASE_URLS, SPECIALTIES, OUTPUT_FILE_PATH
from utils.logger import app_logger

async def main():
    """
    Main orchestration function to run the scraping process.
    """
    start_time = time.time()
    app_logger.info("--- Starting URL Scraping Agent ---")
    
    # Initialize all scrapers
    scrapers = [
        PractoScraper(BASE_URLS["practo"]),
        JustdialScraper(BASE_URLS["justdial"]),
        # Add other scraper instances here as they are built
    ]
    
    # Create a list of all scraping tasks to run concurrently
    tasks = []
    for scraper in scrapers:
        for specialty in SPECIALTIES:
            tasks.append(scraper.scrape(specialty))

    # Run tasks concurrently with a progress bar
    all_found_urls = []
    results = await tqdm.gather(*tasks, desc="Scraping All Specialties")
    
    for url_list in results:
        all_found_urls.extend(url_list)

    # --- Data Deduplication and Saving ---
    if not all_found_urls:
        app_logger.warning("No URLs were found. Exiting.")
        return

    app_logger.info(f"Total URLs found before deduplication: {len(all_found_urls)}")
    
    # Use pandas for efficient deduplication
    df = pd.DataFrame(all_found_urls, columns=['url'])
    df.drop_duplicates(inplace=True)
    
    unique_urls_count = len(df)
    app_logger.info(f"Total unique URLs after deduplication: {unique_urls_count}")
    
    # Save the unique URLs to a CSV file
    try:
        df.to_csv(OUTPUT_FILE_PATH, index=False)
        app_logger.success(f"Successfully saved {unique_urls_count} unique URLs to {OUTPUT_FILE_PATH}")
    except Exception as e:
        app_logger.error(f"Failed to save URLs to file: {e}")

    # Gracefully close all scraper sessions
    for scraper in scrapers:
        await scraper.close_session()

    end_time = time.time()
    app_logger.info(f"--- URL Scraping Agent Finished in {end_time - start_time:.2f} seconds ---")


if __name__ == "__main__":
    asyncio.run(main())