import asyncio
from playwright.async_api import async_playwright

async def test_contact_click():
    """Test clicking Call Now button on a specific URL."""
    test_url = "https://www.practo.com/pune/doctor/deepak-89-psychiatrist?practice_id=1434262&specialization=Psychiatrist&referrer=doctor_listing&page_uid=f27e3269-aee6-4e38-b184-fb659687448"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to False to see browser
        page = await browser.new_page()
        
        print("Loading page...")
        await page.goto(test_url, wait_until='domcontentloaded')
        await page.wait_for_timeout(3000)
        
        # Try clicking Call Now button
        print("Looking for Call Now button...")
        try:
            call_button = await page.wait_for_selector('button:has-text("Call Now")', timeout=5000)
            if call_button:
                print("Found Call Now button, clicking...")
                await call_button.click()
                await page.wait_for_timeout(3000)
                
                # Check if phone number appeared
                html_content = await page.content()
                if '+91' in html_content:
                    print("✓ Phone number found after clicking!")
                    import re
                    phones = re.findall(r'\+91\d{10}', html_content)
                    print(f"Phone numbers found: {phones}")
                else:
                    print("✗ No phone number found after clicking")
        except:
            print("Call Now button not found")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_contact_click())
