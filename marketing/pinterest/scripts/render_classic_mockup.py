"""Renders the Classic style mockup for the landing page hero."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent.parent
SOURCE = ROOT / "public/landing/Mockups/classic_mockup_source.html"
OUTPUT = ROOT / "public/landing/Mockups/Classic_Style_City_Cel_Mockup.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 768, "height": 1365},
            device_scale_factor=2,
        )
        await page.goto(SOURCE.as_uri())
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=str(OUTPUT), full_page=False)
        await browser.close()
    print(f"Saved: {OUTPUT}")

asyncio.run(main())
