import pypdf
import os

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\testes\Student_Understanding_Model_Sheet_Fillable.pdf"
reader = pypdf.PdfReader(pdf_path)
fields = reader.get_fields()

print("--- NAME/STUDENT RELATED FIELDS ---")
for name, field in fields.items():
    name_lower = name.lower()
    if "name" in name_lower or "stud" in name_lower:
        val = field.get('/V')
        print(f"Field: {name} -> Value: {repr(val)}, Type: {field.get('/FT')}")
