import requests
import datetime

class DiscoverClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://widgetapi.discoverchildcare.co.nz"

    def get_token(self):
        url = f"{self.base_url}/api/EnrolmentForm/GetToken?centreToken={self.api_key}"
        print(f"🚀 Sending GET to: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print("❌ Error getting token:", e)
            return None

    def get_staff_hours(self, token):
        url = f"{self.base_url}/api/Report/GetStaffHoursByActivity"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        payload = {
            "FromDate": None,
            "ToDate": None,
            "CentreId": None
        }
        try:
            print(f"📊 Sending POST to: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("❌ Staff Hours Error:", e)
            return None

    def get_centre_funding(self, token, month: str):
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        start_date = f"{month}-01"
        year, month_num = map(int, month.split("-"))
        next_month = datetime.date(year, month_num, 28) + datetime.timedelta(days=4)
        last_day = (next_month - datetime.timedelta(days=next_month.day)).day
        end_date = f"{month}-{last_day}"

        payload = {
            "FromDate": start_date,
            "ToDate": end_date
        }

        url = f"{self.base_url}/api/Report/GetCentreFunding"
        try:
            print(f"💰 Fetching Centre Funding from {start_date} to {end_date}")
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("❌ Centre Funding Error:", e)
            return None


# ⬇️ This function connects your backend to the live Discover data
def get_discover_data(centre_name: str):
    from futurefocus_backend.companies import company_config  # ensure correct path

    try:
        api_key = company_config[centre_name]["api_key"]
    except KeyError:
        print(f"❌ No API key configured for: {centre_name}")
        return None

    client = DiscoverClient(api_key)
    token = client.get_token()
    if not token:
        return None

    today = datetime.date.today()
    this_month = today.strftime("%Y-%m")
    funding_data = client.get_centre_funding(token, this_month)

    if not funding_data:
        print(f"⚠️ No funding data returned for {centre_name}")
        return None

    # 🔍 Print raw funding data for inspection
    print(f"📦 Raw funding data for {centre_name}:\n", funding_data)

    try:
        under_2 = 0
        over_2 = 0

        for item in funding_data:
            age_group = item.get("AgeGroup", "").lower()
            hours = item.get("Hours", 0)

            if "under" in age_group or "u2" in age_group:
                under_2 += hours
            elif "over" in age_group or "o2" in age_group:
                over_2 += hours

        working_days = len(set(item["Date"] for item in funding_data if "Date" in item))

        return {
            "Under 2": under_2,
            "Over 2": over_2,
            "working_days": working_days,
            "total": under_2 + over_2
        }

    except Exception as e:
        print(f"❌ Error parsing funding data for {centre_name}:", e)
        return None
