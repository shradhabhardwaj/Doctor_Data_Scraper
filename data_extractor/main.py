# data_extractor/main.py (FINAL VERSION)

import asyncio
import pandas as pd
import json
import os
from tqdm.asyncio import tqdm
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from httpx import AsyncClient

from .scrapers.profile_scraper import ProfileScraper
from .processors.data_processor import DataProcessor
from .utils.config import INPUT_URL_FILE, OUTPUT_PROCESSED_FILE, OUTPUT_RAW_FILE
from .utils.logger import app_logger

# Define a semaphore to limit concurrent geocoding requests
geocoding_semaphore = asyncio.Semaphore(2)

async def scrape_single_url(context, url: str) -> dict:
    """Fetches and scrapes a single URL using a headless browser."""
    page = None
    try:
        page = await context.new_page()
        # Navigate and wait for the DOM to be ready
        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        # Wait for a reliable element to appear on the page
        await page.wait_for_selector("div.c-profile--clinic--item", timeout=20000)
        
        html_content = await page.content()
        scraper = ProfileScraper(html_content)
        raw_data = scraper.extract_data()
        raw_data['source_url'] = url
        return {"url": url, "status": "scraped", "raw_data": raw_data}
    except PlaywrightTimeoutError:
        app_logger.error(f"Timeout waiting for content on {url}. Skipping.")
        return {"url": url, "status": "timeout_error", "raw_data": None}
    except Exception as e:
        app_logger.error(f"Failed to scrape {url}: {e}")
        return {"url": url, "status": "fetch_failed", "raw_data": None}
    finally:
        if page and not page.is_closed():
            await page.close()

async def process_record(raw_record: dict, geo_client: AsyncClient) -> dict | None:
    """Wrapper to process a single record under semaphore control."""
    # Ensure raw_record is not None before processing
    if not raw_record:
        return None
    async with geocoding_semaphore:
        processor = DataProcessor(raw_record, raw_record.get('source_url', ''))
        return await processor.process(geo_client)

async def main():
    start_time = time.time()
    app_logger.info("--- Starting Final Data Extraction & Processing Run (Module 2) ---")
    
    try:
        urls_df = pd.read_csv(INPUT_URL_FILE)
        urls_to_scrape = urls_df['url'].tolist()
    except FileNotFoundError:
        app_logger.error(f"Input file not found: {INPUT_URL_FILE}. Run Module 1.")
        return

    all_raw_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        tasks = [scrape_single_url(context, url) for url in urls_to_scrape]
        scrape_results = await tqdm.gather(*tasks, desc="Scraping All Profiles")
        
        await browser.close()

    all_raw_data = [res['raw_data'] for res in scrape_results if res and res.get('raw_data')]
    
    with open(OUTPUT_RAW_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_raw_data, f, indent=4, ensure_ascii=False)
    app_logger.success(f"Saved {len(all_raw_data)} raw records to {OUTPUT_RAW_FILE}")

    app_logger.info(f"Now processing {len(all_raw_data)} records...")
    
    async with AsyncClient(http2=True) as geo_client:
        tasks = [process_record(record, geo_client) for record in all_raw_data]
        process_results = await tqdm.gather(*tasks, desc="Validating and Cleaning Data")

    successful_processed_data = [data for data in process_results if data]
    skipped_records = len(all_raw_data) - len(successful_processed_data)

    app_logger.info(f"--- Processing Complete ---")
    app_logger.info(f"Successfully processed and validated: {len(successful_processed_data)} doctors")
    app_logger.info(f"Skipped or invalid: {skipped_records} records")

    with open(OUTPUT_PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(successful_processed_data, f, indent=4, ensure_ascii=False)
    app_logger.success(f"Saved {len(successful_processed_data)} processed records to {OUTPUT_PROCESSED_FILE}")

    end_time = time.time()
    app_logger.info(f"--- Agent Finished in {end_time - start_time:.2f} seconds ---")

if __name__ == "__main__":
    asyncio.run(main())