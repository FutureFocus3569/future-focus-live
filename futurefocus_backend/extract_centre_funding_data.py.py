import pdfplumber
import re

def extract_occupancy_from_pdf(pdf_path: str) -> dict:
    data = {}
    centre_name = "Terrace Views"

    total_under2 = 0
    total_over2 = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.splitlines():
                # Match lines that include daily attendance: U2, O2, 20 Hrs, Plus 10 ECE
                match = re.match(r"^(Mon|Tue|Wed|Thu|Fri)\s\d{2}-[A-Za-z]{3}.*?(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line)
                if match:
                    _, u2, o2, h20, plus10 = match.groups()
                    total_under2 += int(u2)
                    total_over2 += int(o2) + int(h20) + int(plus10)

    total = total_under2 + total_over2
    data[centre_name] = {
        "u2": total_under2,
        "o2": total_over2,
        "total": total
    }
    return data

# For standalone test:
if __name__ == "__main__":
    result = extract_occupancy_from_pdf("exports/Terrace Views/2025-05.pdf")
    print(result)
