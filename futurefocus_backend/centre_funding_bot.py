from datetime import datetime
import os
import io
import re
import pdfplumber
from google.cloud import storage

# 🔐 Cloud Storage configuration
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME") or "futurefocus-centre-reports"

# 👶 Centre configurations (licensing)
CENTRES = {
    "Terrace Views": {"total_licence": 100, "u2_licence": 30},
    "Papamoa Beach": {"total_licence": 80, "u2_licence": 20},
    "The Boulevard": {"total_licence": 82, "u2_licence": 25},
    "The Bach": {"total_licence": 50, "u2_licence": 19},
    "Livingstone Drive": {"total_licence": 82, "u2_licence": 16}
}

# 🧠 Occupancy logic
def fetch_occupancy_data():
    results = {}
    WORKING_DAYS = 22
    HOURS_PER_DAY = 6
    current_month = datetime.now().strftime("%Y-%m")

    print(f"🕵️ Fetching occupancy data for {current_month}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    for centre_name, config in CENTRES.items():
        blob_path = f"{centre_name}/{current_month}.pdf"
        blob = bucket.blob(blob_path)

        print(f"📦 Checking GCS blob: {blob_path}")
        if not blob.exists():
            print(f"⚠️ PDF not found for {centre_name}, skipping...")
            results[centre_name] = {"u2": 0, "o2": 0, "total": 0}
            continue

        u2_total_hours = 0
        o2_total_hours = 0
        data_found = False

        with io.BytesIO(blob.download_as_bytes()) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue

                    print(f"\n📄 PDF Page Text ({centre_name}):\n{text}\n{'-' * 40}")

                    for line in text.splitlines():
                        clean_line = line.strip().lower()
                        print(f"🔍 Analyzing: {repr(line)}")

                        if "under 2" in clean_line:
                            match = re.findall(r"\d+", line)
                            if match:
                                u2_total_hours = int(match[-1])
                                data_found = True
                                print(f"✅ Found Under 2: {u2_total_hours}")

                        elif any(k in clean_line for k in ["over 2", "plus 10 ece", "20 hours"]):
                            match = re.findall(r"\d+", line)
                            if match:
                                o2_total_hours += int(match[-1])
                                data_found = True
                                print(f"✅ Found Over 2-type: {o2_total_hours}")

        if not data_found:
            print(f"❌ No valid data found in PDF for {centre_name}")
            results[centre_name] = {"u2": 0, "o2": 0, "total": 0}
            continue

        u2_cap = config["u2_licence"] * WORKING_DAYS * HOURS_PER_DAY
        o2_cap = (config["total_licence"] - config["u2_licence"]) * WORKING_DAYS * HOURS_PER_DAY
        total_cap = config["total_licence"] * WORKING_DAYS * HOURS_PER_DAY

        results[centre_name] = {
            "u2": round((u2_total_hours / u2_cap) * 100) if u2_cap else 0,
            "o2": round((o2_total_hours / o2_cap) * 100) if o2_cap else 0,
            "total": round(((u2_total_hours + o2_total_hours) / total_cap) * 100) if total_cap else 0,
        }

        print(f"📊 Final % for {centre_name}: {results[centre_name]}")

    return results
