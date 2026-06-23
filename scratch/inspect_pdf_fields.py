import pypdf

pdf_path = "docs/Student Understanding Model Sheet - Fillable (English).pdf"
reader = pypdf.PdfReader(pdf_path)

print("--- Inspecting fields ---")
fields = reader.get_fields()
if not fields:
    print("No form fields found!")
else:
    for name, field in fields.items():
        print(f"Field: {name}, Type: {field.get('/FT')}")
