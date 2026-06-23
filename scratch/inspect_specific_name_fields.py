import pypdf

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\testes\Student_Understanding_Model_Sheet_Fillable.pdf"
reader = pypdf.PdfReader(pdf_path)

catalog = reader.trailer['/Root']
acro_form = catalog['/AcroForm']
fields = acro_form['/Fields']

print(f"Total fields: {len(fields)}")
for idx, f_ref in enumerate(fields):
    f = f_ref.get_object()
    name = f.get('/T')
    val = f.get('/V')
    if name in ['student_name', 'student_name_reading']:
        print(f"Index: {idx}, Name: {repr(name)}, Value: {repr(val)}")
        if '/Kids' in f:
            print("  Has kids:")
            for kid_ref in f['/Kids']:
                kid = kid_ref.get_object()
                print(f"    Kid name: {repr(kid.get('/T'))}, Value: {repr(kid.get('/V'))}")
