from services.llm_service import structure_raw_text
from test_pdf import extract

path = "uploads/d1f48193-4db7-4d07-8bb4-c95c46acc752_sterling-accuris-pathology-sample-report-unlocked.pdf"
raw_text = extract(path)
print("Raw text length:", len(raw_text))

print("Calling structure_raw_text...")
result = structure_raw_text(raw_text)
if not result:
    print("Result is empty or None!")
else:
    print("Success! Extracted lines:", len(result.split('\n')))
