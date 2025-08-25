# data_extractor/main.py

import asyncio
import pandas as pd
import json
import os
import time
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from httpx import AsyncClient

from .scrapers.profile_scraper import ProfileScraper
from .processors.data_processor import DataProcessor
from .utils.config import INPUT_URL_FILE, OUTPUT_RAW_FILE, OUTPUT_PROCESSED_FILE
from .utils.logger import app_logger

from .exporters.data_exporter import run_export
from .utils.config import EXPORT_CSV_FILE, EXPORT_EXCEL_FILE, TEST_LIMIT



# Limit concurrent geocoding calls
geocoding_semaphore = asyncio.Semaphore(2)


async def scrape_single_url(context, url: str) -> dict:
    """Fetches and scrapes a single URL with contact button clicking."""
    page = None
    try:
        page = await context.new_page()
        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        await page.wait_for_selector("div.c-profile--clinic--item", timeout=20000)
        
        # Click “Call Now” if present
        try:
            call_button = await page.wait_for_selector('button:has-text("Call Now")', timeout=5000)
            if call_button:
                await call_button.click()
                await page.wait_for_timeout(2000)
        except:
            pass
        
        html_content = await page.content()
        scraper = ProfileScraper(html_content, debug_mode=False, save_debug_html=False)
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
    """Process a single record under semaphore control."""
    if not raw_record:
        return None
    async with geocoding_semaphore:
        processor = DataProcessor(raw_record, raw_record.get('source_url', ''))
        return await processor.process(geo_client)


async def main():
    start_time = time.time()
    app_logger.info("--- Testing Contact Extraction on Small Dataset ---")
    
    try:
        urls_df = pd.read_csv(INPUT_URL_FILE)
        all_urls = urls_df['url'].tolist()
        # Apply TEST_LIMIT
        if TEST_LIMIT:
            urls_to_scrape = all_urls[:TEST_LIMIT]
            app_logger.info(f"TEST_LIMIT={TEST_LIMIT}; testing on first {TEST_LIMIT} URLs")
        else:
            urls_to_scrape = all_urls
        
        
            #urls_to_scrape = urls_df['url'].tolist()  # Full dataset (or [:5] for small test)
            app_logger.info(f"Testing contact extraction on {len(urls_to_scrape)} URLs")
    except FileNotFoundError:
        app_logger.error(f"Input file not found: {INPUT_URL_FILE}")
        return
    except Exception as e:
        app_logger.error(f"Error reading URL file: {e}")
        return

    all_raw_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        tasks = [scrape_single_url(context, url) for url in urls_to_scrape]
        scrape_results = await tqdm.gather(*tasks, desc="Testing Contact Extraction")
        await browser.close()

    all_raw_data = [res['raw_data'] for res in scrape_results if res and res.get('raw_data')]
    test_file = "output/test_contact_extraction.json"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(all_raw_data, f, indent=4, ensure_ascii=False)
    app_logger.success(f"Saved {len(all_raw_data)} test records to {test_file}")

    contact_success = sum(1 for record in all_raw_data if record.get('contact_number'))
    app_logger.info(f"Contact extraction success: {contact_success}/{len(all_raw_data)} records")

    print("\n=== SAMPLE RESULTS ===")
    for i, record in enumerate(all_raw_data[:3]):
        print(f"Record {i+1}:")
        print(f"  Doctor: {record.get('doctor_name')}")
        print(f"  Contact: {record.get('contact_number')}")
        print(f"  Contact Type: {record.get('contact_type')}")
        print(f"  Email: {record.get('contact_email')}")
        print(f"  Email Type: {record.get('email_type')}")
        print(f"  Recommendation: {record.get('recommendation_percent')}%")
        print()

    if all_raw_data:
        app_logger.info(f"Processing {len(all_raw_data)} records...")
        async with AsyncClient(http2=True) as geo_client:
            tasks = [process_record(record, geo_client) for record in all_raw_data]
            process_results = await tqdm.gather(*tasks, desc="Processing Test Data")

        successful_processed_data = [data for data in process_results if data]
        processed_file = "output/test_structured_doctor_data.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(successful_processed_data, f, indent=4, ensure_ascii=False)
        app_logger.success(f"Saved {len(successful_processed_data)} processed records to {processed_file}")

        # ─────────── ADD EXPORT CALL ───────────
        run_export(
            raw_json_path        = test_file,
            structured_json_path = processed_file,
            output_excel_path    = EXPORT_EXCEL_FILE,
            test_limit           = 10       # only first 10 records
        )
        # ────────────────────────────────────────

    end_time = time.time()
    app_logger.info(f"--- Test completed in {end_time - start_time:.2f} seconds ---")


if __name__ == "__main__":
    asyncio.run(main())
