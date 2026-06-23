import pypdf
import os
import sys

# Ensure parent directory is in sys.path
sys.path.insert(0, r"c:\Users\mathe\Documents\mestrado\Onotlogia\python")

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\testes\Student_Understanding_Model_Sheet_Fillable.pdf"
print(f"File exists: {os.path.exists(pdf_path)}")

print("--- PYPDF ALL FIELDS ---")
reader = pypdf.PdfReader(pdf_path)
fields = reader.get_fields()
if fields:
    for name, field in fields.items():
        val = field.get('/V')
        print(f"Field: {name} -> Value: {repr(val)}, Type: {field.get('/FT')}")
else:
    print("No AcroForm fields found.")

print("\n--- PDFPARSER.PY PARSE_PDF_FORM ---")
from pdf_parser import parse_pdf_form
try:
    res = parse_pdf_form(pdf_path)
    print("Result:")
    for k, v in res.items():
        print(f"  {k}: {repr(v)}")
except Exception as e:
    import traceback
    traceback.print_exc()
