import os
import pdfplumber

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\docs\Student Understanding and Support Sheet - Example Form (English).pdf"

if not os.path.exists(pdf_path):
    print("PDF not found at:", pdf_path)
else:
    print("Reading PDF using pdfplumber...")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n--- PAGE {i+1} ---")
            text = page.extract_text()
            print(text[:1500]) # print first 1500 chars
            
            # Print tables if found
            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} tables on page {i+1}:")
                for j, table in enumerate(tables):
                    print(f"Table {j+1}:")
                    for row in table[:5]: # print first 5 rows
                        print("  ", row)
