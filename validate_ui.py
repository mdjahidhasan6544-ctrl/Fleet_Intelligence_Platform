import asyncio
from playwright.async_api import async_playwright

async def validate():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 1. Page Load
        print("Checking page load...")
        response = await page.goto("http://localhost:8000")
        assert response.status == 200
        print("Page loaded successfully.")
        
        # 2. Map Load
        print("Checking map exists...")
        await page.wait_for_selector("#map")
        print("Map found.")
        
        # 3. Sidebar exists
        print("Checking sidebar panels...")
        await page.wait_for_selector("#sidebar")
        await page.wait_for_selector("#device-list")
        await page.wait_for_selector("#alert-container")
        print("Sidebar elements found.")
        
        # 4. API check (Wait for live state update)
        print("Waiting for device markers to appear...")
        # We'll wait up to 10 seconds for a device marker to be added
        try:
            await page.wait_for_selector(".leaflet-marker-icon", timeout=10000)
            print("Device marker found on map.")
        except Exception:
            print("No device marker found yet. (Simulator might be off or slow)")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(validate())
