import sys
import os

sys.path.append(os.path.abspath("."))
from pdf_parser import parse_pdf_form

pdf_path = "testes/Student_Understanding_Model_Sheet_Fillable.pdf"
print(f"Parsing: {pdf_path}")
try:
    data = parse_pdf_form(pdf_path)
    print("\nParsed Data:")
    for k, v in data.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"Error parsing: {e}")
