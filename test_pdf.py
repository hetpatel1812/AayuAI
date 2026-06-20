import os
import pdfplumber

def extract(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error: {e}"

path = "uploads/d1f48193-4db7-4d07-8bb4-c95c46acc752_sterling-accuris-pathology-sample-report-unlocked.pdf"
print("Extracting...")
res = extract(path)
print(f"Extracted length: {len(res)}")
if len(res) < 500:
    print(res)
