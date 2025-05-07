import pdfplumber
import os

centres = [
    "Terrace Views",
    "Papamoa Beach",
    "The Boulevard",
    "The Bach",
    "Livingstone Drive",
]

current_month = "2025-05"  # Or use datetime.now().strftime("%Y-%m")
EXPORT_ROOT = "exports"

for centre_name in centres:
    print(f"\n📄 Debugging: {centre_name}")
    pdf_path = os.path.join(EXPORT_ROOT, centre_name, f"{current_month}.pdf")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        continue

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            print(f"\n--- Page {page_number} ---")
            if text:
                print(text)
            else:
                print("⚠️ No text extracted from this page.")
    
    print("-" * 80)
