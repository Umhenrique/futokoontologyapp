import pypdf

def extract_acroform_fields(fields_list, form_data=None):
    if form_data is None:
        form_data = {}
    for f_ref in fields_list:
        f = f_ref.get_object()
        name = f.get('/T')
        val = f.get('/V')
        
        # If it has kids, traverse them recursively
        if '/Kids' in f:
            extract_acroform_fields(f['/Kids'], form_data)
        
        if name:
            name_str = str(name).strip()
            if val:
                val_str = str(val).strip()
                if val_str:
                    # Do not overwrite a non-empty value with an empty value
                    if name_str not in form_data or not form_data[name_str]:
                        form_data[name_str] = val_str
            else:
                # If not in form_data yet, initialize it as empty string
                if name_str not in form_data:
                    form_data[name_str] = ""
    return form_data

pdf_path = r"c:\Users\mathe\Documents\mestrado\Onotlogia\python\testes\Student_Understanding_Model_Sheet_Fillable.pdf"
reader = pypdf.PdfReader(pdf_path)
catalog = reader.trailer['/Root']
form_data = {}
if '/AcroForm' in catalog and '/Fields' in catalog['/AcroForm']:
    form_data = extract_acroform_fields(catalog['/AcroForm']['/Fields'])

print("student_name in form_data:", repr(form_data.get("student_name")))
print("student_name_reading in form_data:", repr(form_data.get("student_name_reading")))
print("school_name_elementary in form_data:", repr(form_data.get("school_name_elementary")))
