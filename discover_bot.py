import asyncio
from playwright.async_api import async_playwright

EMAIL = "courtney@futurefocus.co.nz"
PASSWORD = "Mercedes2!!!"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True to hide browser
        context = await browser.new_context()
        page = await context.new_page()

        # Go to the login page
        await page.goto("https://discoverchildcare.co.nz/Account/Login")

        # Fill in login credentials
        await page.fill("input#Email", EMAIL)
        await page.fill("input#Password", PASSWORD)

        # Click login
        await page.click("button:has-text('Sign in')")

        # Wait for the dashboard to appear
        await page.wait_for_selector("text=Centre List", timeout=10000)
        print("✅ Logged in successfully!")

        # Click the current centre to open selector
        await page.click("div.user-centre > span")
        await page.wait_for_selector("text=Centre List")
        await page.click("text=Future Focus - Papamoa Beach")
        print("🏫 Centre switched to Papamoa Beach!")

        # Optional: wait for dashboard to fully render
        await asyncio.sleep(3)

        # 🔽 Navigate to Centre Funding Report
        print("➡️ Clicking 'Reports' in sidebar...")
        await page.locator("nav >> text=Reports").first.click()
        await asyncio.sleep(1)

        print("➡️ Clicking 'Finance Reports'...")
        await page.locator("text=Finance Reports").first.click()
        await asyncio.sleep(1)

        print("➡️ Clicking 'Centre Funding'...")
        await page.locator("text=Centre Funding").first.click()

        await page.wait_for_selector("text=Centre Funding")
        print("📄 Centre Funding report loaded!")

        # Keep browser open to verify
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(run())
