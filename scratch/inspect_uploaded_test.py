import pypdf
import pdfplumber

pdf_path = "testes/Student_Understanding_Model_Sheet_Fillable.pdf"
print(f"Reading: {pdf_path}")

# Check with pypdf
reader = pypdf.PdfReader(pdf_path)
fields = reader.get_fields()
print(f"AcroForm Fields Found: {len(fields) if fields else 0}")
if fields:
    for name, field in fields.items():
        val = field.get('/V')
        if val:
            print(f"  Field: {name} -> Value: {repr(val)}")

# Check with pdfplumber raw text extraction
print("\n--- pdfplumber raw text extraction (Page 1) ---")
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()
    print("Raw Text:", repr(text))
