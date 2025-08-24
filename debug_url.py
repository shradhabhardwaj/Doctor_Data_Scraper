# debug_url.py

import asyncio
from playwright.async_api import async_playwright
import os

# A URL that we know was failing from your previous logs
URL_TO_DEBUG = "https://www.practo.com/pune/doctor/dr-zutshi-dhananjay-vikram-cardiologist?practice_id=1423609&specialization=Cardiologist&referrer=doctor_listing&page_uid=b222c0f3-eb9e-47bb-8499-4864058bc3a2"

async def main():
    print("--- Starting Forensic HTML Capture ---")
    
    # Create a directory for the output if it doesn't exist
    os.makedirs("debug_html", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Navigating to: {URL_TO_DEBUG}")
        try:
            await page.goto(URL_TO_DEBUG, timeout=60000, wait_until='networkidle')
            html_content = await page.content()
            
            filepath = os.path.join("debug_html", "failed_page_content.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"SUCCESS: Saved the exact HTML to '{filepath}'")
            
        except Exception as e:
            print(f"ERROR: An exception occurred: {e}")
        finally:
            await browser.close()
            
    print("--- Forensic Capture Complete ---")

if __name__ == "__main__":
    asyncio.run(main())