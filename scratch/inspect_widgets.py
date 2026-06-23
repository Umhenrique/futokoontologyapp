import pypdf

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\testes\Student_Understanding_Model_Sheet_Fillable.pdf"
reader = pypdf.PdfReader(pdf_path)

# Let's inspect the fields and their Kids/V entries
fields = reader.get_fields()
print("Fields keys:", list(fields.keys()))

print("\n--- DETAILED WIDGET INSPECTION ---")
# Let's check fields from the document catalog /AcroForm/Fields
catalog = reader.trailer['/Root']
if '/AcroForm' in catalog:
    acro_form = catalog['/AcroForm']
    if '/Fields' in acro_form:
        for idx, f_ref in enumerate(acro_form['/Fields']):
            f = f_ref.get_object()
            t = f.get('/T')
            v = f.get('/V')
            print(f"Field {idx}: Name={repr(t)}, Value={repr(v)}")
            if '/Kids' in f:
                print(f"  Field {t} has Kids:")
                for k_ref in f['/Kids']:
                    k = k_ref.get_object()
                    print(f"    Kid: Name={repr(k.get('/T'))}, Value={repr(k.get('/V'))}")
else:
    print("No AcroForm found in catalog.")
