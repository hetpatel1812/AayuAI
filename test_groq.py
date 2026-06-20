from services.llm_service import structure_raw_text, get_explanation

print("Testing structure_raw_text:")
res = structure_raw_text("Hemoglobin 13.5 g/dL 12-15")
print(f"Result: {res}")

print("\nTesting get_explanation:")
res2 = get_explanation({'test': 'Hemoglobin', 'value': '13.5', 'unit': 'g/dL', 'status': 'NORMAL'}, 'en')
print(f"Result: {res2}")
