import pdfplumber
import os

def clean_text(val):
    if val is None:
        return ""
    return str(val).strip().replace("\n", " ")

def parse_pdf_form(pdf_path):
    """
    Parses a Student Understanding / Support Sheet PDF and returns a dictionary of extracted data.
    """
    data = {
        "student_name": "",
        "gender": "",
        "school_name": "",
        "grade": "",
        "class_name": "",
        "homeroom_teacher": "",
        "administrator": "",
        "absent_days": 30, # Default minimum
        "support_facility": "",
        "facility_type": "EducationSupportCenter", # Default fallback
    }

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")

    # 1. Try extracting via pypdf AcroForm fields first (for filled interactive forms)
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        
        # Traverse catalog fields directly to prevent duplicate field names from overwriting populated values
        form_data = {}
        has_form_data = False
        
        def extract_acroform_fields(fields_list):
            nonlocal has_form_data
            for f_ref in fields_list:
                f = f_ref.get_object()
                name = f.get('/T')
                val = f.get('/V')
                
                if '/Kids' in f:
                    extract_acroform_fields(f['/Kids'])
                
                if name:
                    name_str = str(name).strip()
                    if val:
                        val_str = str(val).strip()
                        if val_str:
                            # Keep the first non-empty value for duplicate field names
                            if name_str not in form_data or not form_data[name_str]:
                                form_data[name_str] = val_str
                                has_form_data = True
                    else:
                        if name_str not in form_data:
                            form_data[name_str] = ""

        catalog = reader.trailer['/Root']
        if '/AcroForm' in catalog and '/Fields' in catalog['/AcroForm']:
            extract_acroform_fields(catalog['/AcroForm']['/Fields'])
            
        # Fallback to standard get_fields() if catalog traversal found nothing
        if not form_data:
            fields = reader.get_fields()
            if fields:
                for name, field in fields.items():
                    val = field.get('/V')
                    if val:
                        val_str = str(val).strip()
                        if val_str:
                            form_data[name] = val_str
                            has_form_data = True
                            
        if has_form_data:
                # Map fields to our expected data structure
                for k in data.keys():
                    if k in form_data:
                        if k == "absent_days":
                            try:
                                data[k] = int(form_data[k])
                            except ValueError:
                                pass
                        else:
                            data[k] = form_data[k]
                
                # 1. Fallback for student_name
                if not data["student_name"] and "student_name_reading" in form_data:
                    data["student_name"] = form_data["student_name_reading"]
                
                # 2. Fallback for school_name
                if not data["school_name"]:
                    if "school_name_elementary" in form_data:
                        data["school_name"] = form_data["school_name_elementary"]
                    elif "school_name_middle" in form_data:
                        data["school_name"] = form_data["school_name_middle"]
                    elif "school_name_high" in form_data:
                        data["school_name"] = form_data["school_name_high"]
                
                # 3. Fallback for homeroom_teacher
                if not data["homeroom_teacher"]:
                    if "added_by_staff" in form_data:
                        data["homeroom_teacher"] = form_data["added_by_staff"]
                    elif "created_by_staff" in form_data:
                        data["homeroom_teacher"] = form_data["created_by_staff"]
                
                # 4. Fallback for administrator
                if not data["administrator"]:
                    if "created_by_staff" in form_data:
                        data["administrator"] = form_data["created_by_staff"]
                    elif "added_by_staff" in form_data:
                        data["administrator"] = form_data["added_by_staff"]
                
                # 5. Fallback for absent_days (max of abs_days_5_*)
                if data["absent_days"] == 30 or not data["absent_days"]:
                    grade_absences = []
                    for name, val_str in form_data.items():
                        if name.startswith("abs_days_5_"):
                            try:
                                grade_absences.append(int(val_str))
                            except ValueError:
                                pass
                    if grade_absences:
                        data["absent_days"] = max(grade_absences)
                
                # If we got at least student_name, return this parsed data
                if data["student_name"] and data["student_name"] != "Unknown Student":
                    # Fallbacks if other fields are empty
                    if not data["school_name"]:
                        data["school_name"] = "Unknown School"
                    if not data["homeroom_teacher"]:
                        data["homeroom_teacher"] = "Unknown Teacher"
                    if not data["administrator"]:
                        data["administrator"] = "Unknown Administrator"
                    return data
    except Exception as e:
        print(f"Warning: AcroForm extraction failed, falling back to table extraction: {e}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            # Scan all tables on the page
            for table in tables:
                for row in table:
                    # Clean the row elements
                    cleaned_row = [clean_text(cell) for cell in row]
                    
                    # 1. Look for Homeroom Teacher and Administrator
                    # Row: ['Homeroom Teacher (Reading):', 'Teacher A', 'School Administrator:', 'Principal A']
                    for idx, cell in enumerate(cleaned_row):
                        if "Homeroom Teacher" in cell and idx + 1 < len(cleaned_row):
                            data["homeroom_teacher"] = cleaned_row[idx + 1]
                        if "School Administrator" in cell and idx + 1 < len(cleaned_row):
                            data["administrator"] = cleaned_row[idx + 1]

                    # 2. Look for Student Profile Table
                    # Header Row: ['Name (Reading)', 'Gender', 'School Name', 'Grade', 'Class']
                    # Data Row: ['( Reading ) Name', 'Male', 'Oak Elementary', '6th', 'Class 2']
                    if any("Name" in cell and "Reading" in cell for cell in cleaned_row):
                        # The next row in the table usually contains the student values
                        val_idx = table.index(row) + 1
                        if val_idx < len(table):
                            val_row = [clean_text(c) for c in table[val_idx]]
                            # Extract student name (taking the name after \n if present)
                            raw_name_cell = str(table[val_idx][0] or "").strip()
                            if "\n" in raw_name_cell:
                                data["student_name"] = raw_name_cell.split("\n")[-1].strip()
                            else:
                                data["student_name"] = raw_name_cell
                                
                            if len(val_row) > 1:
                                data["gender"] = val_row[1]
                            if len(val_row) > 2:
                                data["school_name"] = val_row[2]
                            if len(val_row) > 3:
                                data["grade"] = val_row[3]
                            if len(val_row) > 4:
                                data["class_name"] = val_row[4]

                    # 3. Look for Support Agencies
                    # If this table has 'Agency Name' in the header row, it is the agencies table
                    if "Agency Name" in cleaned_row:
                        for r in table[1:]:
                            cleaned_r = [clean_text(cell) for cell in r]
                            if len(cleaned_r) >= 3:
                                type_cell = cleaned_r[1]
                                name_cell = cleaned_r[2]
                                if name_cell and name_cell != "None":
                                    if "Support Center" in type_cell or "Support Center" in name_cell:
                                        data["support_facility"] = name_cell
                                        data["facility_type"] = "EducationSupportCenter"
                                    elif "Free School" in type_cell or "Free School" in name_cell:
                                        data["support_facility"] = name_cell
                                        data["facility_type"] = "FreeSchool"
                                    elif "ICT" in type_cell:
                                        data["support_facility"] = name_cell
                                        data["facility_type"] = "HomeICT"
                                    elif "In-School" in type_cell:
                                        data["support_facility"] = name_cell
                                        data["facility_type"] = "InSchoolSupportCenter"

                    # 4. Look for Monthly Absence Record Total
                    # Row: ['Absent Days (incl. official attend.)', '16', '17', '19', '19', '0', '18', '20', '20', '21', '18', '18', '19', '185']
                    if any("Absent Days" in cell for cell in cleaned_row):
                        # The last non-empty element is usually the total
                        non_empty = [c for c in cleaned_row if c != ""]
                        if len(non_empty) > 1:
                            try:
                                val = int(non_empty[-1])
                                # Make sure it is a valid positive number
                                if val > 0:
                                    data["absent_days"] = val
                            except ValueError:
                                pass

    # If support facility was not found in tables, look in page text as fallback
    if not data["support_facility"]:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if "Educational Support Center" in text:
                    data["facility_type"] = "EducationSupportCenter"
                    if "Oak Support Center" in text:
                        data["support_facility"] = "Oak Support Center"
                elif "Free School" in text:
                    data["facility_type"] = "FreeSchool"
                    if "Gainax" in text:
                        data["support_facility"] = "Gainax"

    # Default fallback values if fields are missing
    if not data["student_name"]:
        data["student_name"] = "Unknown Student"
    if not data["school_name"]:
        data["school_name"] = "Unknown School"
    if not data["homeroom_teacher"]:
        data["homeroom_teacher"] = "Unknown Teacher"
    if not data["administrator"]:
        data["administrator"] = "Unknown Administrator"

    return data
