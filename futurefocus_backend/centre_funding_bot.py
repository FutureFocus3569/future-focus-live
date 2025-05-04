from playwright.sync_api import sync_playwright
import os
import datetime

DISCOVER_EMAIL = os.getenv("DISCOVER_EMAIL") or "courtney@futurefocus.co.nz"
DISCOVER_PASSWORD = os.getenv("DISCOVER_PASSWORD") or "Mercedes2!!!"

CENTRE_IDS = {
    "Livingstone Drive": "73668a22-78b9-4b92-b7d0-2e1aaae62f90",
    "Papamoa Beach": "820b4c7b-b24e-464f-9d08-a83f273368ac",
    "The Boulevard": "f1c30c4f-9e6c-4d7c-bc4e-9d88f54749ea",
    "Terrace Views": "1fd6e115-da26-4838-a78d-4804a59e5a94",
    "The Bach": "348d7f06-ab28-4853-9c61-032c9ff1ad22"
}

LICENSE_CONFIG = {
    "Terrace Views": {"total": 100, "u2_cap": 30},
    "Livingstone Drive": {"total": 82, "u2_cap": 16},
    "Papamoa Beach": {"total": 80, "u2_cap": 20},
    "The Boulevard": {"total": 82, "u2_cap": 25},
    "The Bach": {"total": 50, "u2_cap": 19},
}

def fetch_occupancy_data():
    results = {}
    today = datetime.date.today()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://discoverchildcare.co.nz/Account/Login", timeout=30000)
            page.fill("#Email", DISCOVER_EMAIL)
            page.fill("#Password", DISCOVER_PASSWORD)
            page.click("button:has-text('Sign in')")
            page.wait_for_selector("text=Dashboard", timeout=30000)

            for centre_name, centre_id in CENTRE_IDS.items():
                try:
                    print(f"🔍 Fetching data for {centre_name}")
                    page.goto(f"https://discoverchildcare.co.nz/{centre_id}/Home/Index")
                    page.wait_for_selector("text=Reports", timeout=10000)
                    page.click("text=Reports")
                    page.wait_for_selector("text=Finance Reports", timeout=10000)
                    page.click("text=Finance Reports")
                    page.wait_for_timeout(2000)
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(1000)

                    link = page.query_selector('//a[contains(@href, "CenterFunding") and normalize-space(text())="Centre Funding"]')
                    if not link:
                        raise Exception("❌ Could not find Centre Funding link.")
                    page.evaluate("element => element.scrollIntoView()", link)
                    page.wait_for_timeout(500)
                    link.click()

                    page.wait_for_selector("input#GetReport:enabled", timeout=15000)
                    page.click("input#GetReport")
                    page.wait_for_timeout(2000)

                    # 🔧 Updated scroll: leave buffer near bottom
                    page.evaluate("window.scrollTo({ top: document.body.scrollHeight - 600, behavior: 'smooth' })")
                    page.wait_for_timeout(1500)

                    page.wait_for_selector("table#DataTables_Table_0", timeout=20000)

                    def get_total(label):
                        rows = page.query_selector_all("table tbody tr")
                        for row in rows:
                            cells = row.query_selector_all("td")
                            if not cells or len(cells) < 8:
                                continue
                            first_cell_text = cells[0].inner_text().strip().lower()
                            if label.lower() in first_cell_text:
                                value = cells[-1].inner_text().strip().replace(",", "")
                                print(f"✅ Found {label}: {value}")
                                try:
                                    return int(value)
                                except ValueError:
                                    return 0
                        print(f"⚠️ No row found for {label}")
                        return 0

                    u2_total = get_total("Under 2")
                    o2_total = sum(get_total(label) for label in ["Over 2", "20 Hours", "Plus 10 ECE"])

                    license = LICENSE_CONFIG.get(centre_name, {"total": 100, "u2_cap": 30})
                    u2_cap = license["u2_cap"]
                    total_cap = license["total"]

                    final_u2 = min(u2_total, u2_cap)
                    remaining_u2_space = max(0, u2_cap - final_u2)
                    final_o2 = min(o2_total + remaining_u2_space, total_cap - final_u2)

                    occupancy = {
                        "u2": round((final_u2 / total_cap) * 100, 2),
                        "o2": round((final_o2 / total_cap) * 100, 2),
                        "total": round(((final_u2 + final_o2) / total_cap) * 100, 2),
                    }

                    results[centre_name] = occupancy

                except Exception as e:
                    print(f"❌ Error for {centre_name}: {e}")
                    results[centre_name] = {"error": f"{type(e).__name__}: {str(e)}"}

        except Exception as login_error:
            print(f"❌ Login failed: {login_error}")
            for centre in CENTRE_IDS:
                results[centre] = {"error": f"Login failed: {str(login_error)}"}

        finally:
            browser.close()

    print("📊 Final Occupancy Results:", results)
    return results

if __name__ == "__main__":
    fetch_occupancy_data()
