import pypdf
import pdfplumber

# 1. Fill the PDF form using pypdf
reader = pypdf.PdfReader("scratch/test_fillable.pdf")
writer = pypdf.PdfWriter()
writer.append(reader)

# Update fields
writer.update_page_form_field_values(
    writer.pages[0],
    {"student_name": "Alice", "school_name": "Wonderland High"}
)

filled_pdf = "scratch/test_fillable_filled.pdf"
with open(filled_pdf, "wb") as f:
    writer.write(f)
print(f"Generated filled PDF: {filled_pdf}")

# 2. Extract text and tables using pdfplumber to see what it reads
with pdfplumber.open(filled_pdf) as pdf:
    print("\n--- pdfplumber raw text extraction ---")
    text = pdf.pages[0].extract_text()
    print("Raw Text:", repr(text))
    
    print("\n--- pdfplumber tables extraction ---")
    tables = pdf.pages[0].extract_tables()
    for table in tables:
        print("Table:", table)
