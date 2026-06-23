import pypdf

reader = pypdf.PdfReader("scratch/test_fillable_filled.pdf")
fields = reader.get_fields()
for name, field in fields.items():
    print(f"Name: {name}")
    print(f"  Value: {field.get('/V')}")
    print(f"  Field: {field}")
