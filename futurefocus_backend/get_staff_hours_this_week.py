from playwright.sync_api import sync_playwright
import os

DISCOVER_EMAIL = os.getenv("DISCOVER_EMAIL") or "courtney@futurefocus.co.nz"
DISCOVER_PASSWORD = os.getenv("DISCOVER_PASSWORD") or "Mercedes2!!!"

CENTRE_IDS = {
    "Livingstone Drive": "73668a22-78b9-4b92-b7d0-2e1aaae62f90",
    "Papamoa Beach": "820b4c7b-b24e-464f-9d08-a83f273368ac",
    "The Boulevard": "f1c30c4f-9e6c-4d7c-bc4e-9d88f54749ea",
    "Terrace Views": "1fd6e115-da26-4838-a78d-4804a59e5a94",
    "The Bach": "348d7f06-ab28-4853-9c61-032c9ff1ad22"
}

def fetch_staff_hours_this_week_all():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 👈 run invisibly now
        context = browser.new_context()
        page = context.new_page()

        try:
            # ✅ Corrected login selectors
            page.goto("https://discoverchildcare.co.nz/Account/Login", timeout=30000)
            page.wait_for_selector('input#Email', timeout=30000)
            page.fill('input#Email', DISCOVER_EMAIL)
            page.fill('input#Password', DISCOVER_PASSWORD)
            page.click('button:has-text("Sign in")')
            page.wait_for_selector('text=Dashboard', timeout=30000)

            for centre_name, centre_id in CENTRE_IDS.items():
                try:
                    report_url = f"https://discoverchildcare.co.nz/{centre_id}/Reports/StaffHoursByActivity"
                    page.goto(report_url, timeout=30000)
                    page.wait_for_selector("input#GetReport", timeout=30000)
                    page.click("input#GetReport")
                    page.wait_for_timeout(4000)

                    last_cell = page.locator("table tbody tr:last-child td").last
                    hours_text = last_cell.inner_text()
                    results[centre_name] = {"staff_hours": hours_text.strip()}
                except Exception as e:
                    results[centre_name] = {"error": f"{type(e).__name__}: {str(e)}"}
        except Exception as login_error:
            for centre in CENTRE_IDS:
                results[centre] = {"error": f"Login failed: {str(login_error)}"}
        finally:
            browser.close()

    return results
