from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import pdfplumber
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👶 Centre licensing config
CENTRES = {
    "Papamoa Beach": {"total_licence": 80, "u2_licence": 20},
    "Livingstone Drive": {"total_licence": 82, "u2_licence": 16},
    "The Bach": {"total_licence": 50, "u2_licence": 19},
    "Terrace Views": {"total_licence": 100, "u2_licence": 30},
    "The Boulevard": {"total_licence": 82, "u2_licence": 25}
}

# 📅 Defaults
WORKING_DAYS = 22
HOURS_PER_DAY = 6
EXPORT_ROOT = "exports"
BUCKET_NAME = "futurefocus-centre-reports"

def download_from_gcs(centre_name, month_str):
    """Download PDF for a centre/month from GCS if not already cached locally."""
    file_path = os.path.join(EXPORT_ROOT, centre_name, f"{month_str}.pdf")
    if os.path.exists(file_path):
        return file_path

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    blob_path = f"{centre_name}/{month_str}.pdf"
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_path)

    if not blob.exists():
        return None

    blob.download_to_filename(file_path)
    return file_path

@app.get("/occupancy")
def get_occupancy():
    results = {}
    current_month = datetime.now().strftime("%Y-%m")

    for centre, config in CENTRES.items():
        u2_total_hours = 0
        o2_total_hours = 0
        data_found = False

        pdf_path = download_from_gcs(centre, current_month)
        if not pdf_path or not os.path.exists(pdf_path):
            results[centre] = {"u2": 0, "o2": 0, "total": 0}
            continue

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.splitlines()
                for line in lines:
                    if line.startswith("Under 2 "):
                        parts = line.split()
                        u2_total_hours = int(parts[-1])
                        data_found = True
                    elif line.startswith("Over 2 "):
                        parts = line.split()
                        o2_total_hours += int(parts[-1])
                        data_found = True
                    elif line.startswith("Plus 10 ECE"):
                        parts = line.split()
                        o2_total_hours += int(parts[-1])
                    elif line.startswith("20 Hours"):
                        parts = line.split()
                        o2_total_hours += int(parts[-1])

        if not data_found:
            results[centre] = {"u2": 0, "o2": 0, "total": 0}
            continue

        u2_cap = config["u2_licence"] * WORKING_DAYS * HOURS_PER_DAY
        o2_cap = (config["total_licence"] - config["u2_licence"]) * WORKING_DAYS * HOURS_PER_DAY
        total_cap = config["total_licence"] * WORKING_DAYS * HOURS_PER_DAY

        u2_pct = round((u2_total_hours / u2_cap) * 100) if u2_cap else 0
        o2_pct = round((o2_total_hours / o2_cap) * 100) if o2_cap else 0
        total_pct = round(((u2_total_hours + o2_total_hours) / total_cap) * 100) if total_cap else 0

        results[centre] = {"u2": u2_pct, "o2": o2_pct, "total": total_pct}

    return results
